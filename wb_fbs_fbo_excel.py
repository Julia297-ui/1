#!/usr/bin/env python3
"""Excel-отчёт «FBS vs FBO» по детализации финансовых отчётов Wildberries.

Все итоговые листы считаются формулами (SUMIFS) по листу «Детализация», поэтому
при правке строк/формата в детализации сводка пересчитывается сама.

Запуск:
    python3 wb_fbs_fbo_excel.py --file rows.json -o wb_fbs_vs_fbo.xlsx
    WB_API_TOKEN=... python3 wb_fbs_fbo_excel.py 2026-10-19 2026-11-04 -o wb_fbs_vs_fbo.xlsx
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from wb_fbs_fbo_compare import classify, f, fetch

FONT = "Arial"
RUB = '#,##0 ₽;-#,##0 ₽;"–"'
QTY = '#,##0;-#,##0;"–"'
PCT = '0.0%;-0.0%;"–"'
HDR_FILL = PatternFill("solid", start_color="1F3864")
SUB_FILL = PatternFill("solid", start_color="D9E1F2")
KEY_FILL = PatternFill("solid", start_color="FFF2CC")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)

# Колонки листа «Детализация»: (ключ, заголовок, ширина, формат, функция значения)
def _signed(r, field):
    op = r.get("sellerOperName")
    if op == "Продажа":
        return f(r.get(field))
    if op == "Возврат":
        return -f(r.get(field))
    return 0.0


def _loy_sign(r):
    return -1 if r.get("docTypeName") == "Возврат" else 1


DETAIL = [
    ("report", "Отчёт №", 12, "0", lambda r: r.get("reportId")),
    ("dfrom", "Период с", 11, None, lambda r: r.get("dateFrom")),
    ("dto", "Период по", 11, None, lambda r: r.get("dateTo")),
    ("rrdate", "Дата операции", 12, None, lambda r: r.get("rrDate")),
    ("fmt", "Формат", 9, None, lambda r: r["_fmt"]),
    ("op", "Тип операции", 34, None, lambda r: r.get("sellerOperName")),
    ("doc", "Тип документа", 12, None, lambda r: r.get("docTypeName")),
    ("reason", "Основание / вид логистики", 40, None, lambda r: r.get("bonusTypeName")),
    ("vendor", "Артикул продавца", 22, None, lambda r: r.get("vendorCode")),
    ("nm", "Артикул WB (nmId)", 12, "0", lambda r: r.get("nmId") or None),
    ("subject", "Предмет", 14, None, lambda r: r.get("subjectName")),
    ("size", "Размер", 7, None, lambda r: r.get("techSize")),
    ("office", "Склад", 26, None, lambda r: r.get("officeName")),
    ("method", "Способ доставки (WB)", 18, None, lambda r: r.get("deliveryMethod")),
    ("srid", "srid", 18, None, lambda r: r.get("srid")),
    ("sales", "Продажи, шт", 9, QTY,
     lambda r: r.get("quantity", 0) if r.get("sellerOperName") == "Продажа" else 0),
    ("rets", "Возвраты, шт", 9, QTY,
     lambda r: r.get("quantity", 0) if r.get("sellerOperName") == "Возврат" else 0),
    ("rev", "Выручка (цена продавца со скидкой)", 14, RUB, lambda r: _signed(r, "retailPriceWithDisc")),
    ("paid", "Оплатил покупатель", 13, RUB, lambda r: _signed(r, "retailAmount")),
    ("forpay", "К перечислению за товар", 13, RUB, lambda r: _signed(r, "forPay")),
    ("acq", "Эквайринг", 11, RUB,
     lambda r: _signed(r, "acquiringFee") if r.get("sellerOperName") in ("Продажа", "Возврат")
     else (f(r.get("acquiringFee")) if r.get("sellerOperName") == "Корректировка эквайринга" else 0)),
    ("tariff", "Тариф комиссии, %", 9, "0.0", lambda r: f(r.get("commissionPercent")) or None),
    ("tariffw", "Тариф × выручка (служебн.)", 12, "#,##0",
     lambda r: f(r.get("commissionPercent")) * _signed(r, "retailPriceWithDisc")),
    ("otherpay", "Прочие выплаты", 11, RUB,
     lambda r: 0 if r.get("sellerOperName") in ("Продажа", "Возврат") else f(r.get("forPay"))),
    ("addpay", "Доплаты", 10, RUB, lambda r: f(r.get("additionalPayment"))),
    ("logi", "Логистика", 11, RUB, lambda r: f(r.get("deliveryService"))),
    ("rebill", "Возмещение издержек по перемещению", 13, RUB, lambda r: f(r.get("rebillLogisticCost"))),
    ("pvz", "Возмещение за выдачу/возврат на ПВЗ", 13, RUB,
     lambda r: f(r.get("ppvzReward")) if (r.get("sellerOperName") or "").startswith("Возмещение за выдачу") else 0),
    ("pen", "Штраф", 10, RUB, lambda r: f(r.get("penalty"))),
    ("stor", "Хранение", 10, RUB, lambda r: f(r.get("paidStorage"))),
    ("accept", "Приёмка", 10, RUB, lambda r: f(r.get("paidAcceptance"))),
    ("ded", "Удержания", 11, RUB, lambda r: f(r.get("deduction"))),
    ("loy", "Лояльность: баллы и участие", 12, RUB,
     lambda r: _loy_sign(r) * (f(r.get("cashbackAmount")) + f(r.get("cashbackCommissionChange")))),
    ("loycomp", "Компенсация скидки лояльности", 12, RUB,
     lambda r: _loy_sign(r) * f(r.get("cashbackDiscount"))),
]
COL = {k: get_column_letter(i + 1) for i, (k, *_) in enumerate(DETAIL)}


def style_header(ws, row, ncols, height=42):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
        cell.fill = HDR_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BOX
    ws.row_dimensions[row].height = height


def cell(ws, ref, value, fmt=None, bold=False, fill=None, color=None, wrap=False, align=None):
    c = ws[ref]
    c.value = value
    c.font = Font(name=FONT, bold=bold, size=10, color=color)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if wrap or align:
        c.alignment = Alignment(wrap_text=wrap, horizontal=align, vertical="center")
    c.border = BOX
    return c


def build(rows, out):
    classify(rows)
    rows.sort(key=lambda r: (r.get("rrDate") or "", r.get("rrdId") or 0))
    wb = Workbook()
    ws_sum = wb.active
    ws_sum.title = "Сводка"
    ws_pen = wb.create_sheet("Штрафы")
    ws_sku = wb.create_sheet("По артикулам")
    ws_rep = wb.create_sheet("Отчёты")
    ws_det = wb.create_sheet("Детализация")
    ws_m = wb.create_sheet("Методика")

    # ---------- Детализация ----------
    for i, (_, title, width, _, _) in enumerate(DETAIL, 1):
        ws_det.cell(row=1, column=i, value=title)
        ws_det.column_dimensions[get_column_letter(i)].width = width
    style_header(ws_det, 1, len(DETAIL), 54)
    body = Font(name=FONT, size=9)
    for ri, r in enumerate(rows, 2):
        for ci, (_, _, _, fmt, fn) in enumerate(DETAIL, 1):
            v = fn(r)
            if isinstance(v, float):
                v = round(v, 2)
            c = ws_det.cell(row=ri, column=ci, value=v if v != "" else None)
            c.font = body
            if fmt:
                c.number_format = fmt
    last = len(rows) + 1
    ws_det.freeze_panes = "F2"
    ws_det.auto_filter.ref = f"A1:{get_column_letter(len(DETAIL))}{last}"
    ws_det[f"{COL['fmt']}1"].comment = Comment(
        "FBO = FBW (склады WB), FBS = со склада продавца, «—» = не зависит от формата "
        "или не удалось определить. Как определяется — см. лист «Методика».", "Отчёт")

    def rng(key):
        return f"Детализация!${COL[key]}$2:${COL[key]}${last}"

    def sumf(key, fmt_ref, *extra):
        cond = "".join(f",{a},{b}" for a, b in extra)
        return f"SUMIFS({rng(key)},{rng('fmt')},{fmt_ref}{cond})"

    # ---------- Сводка ----------
    ws = ws_sum
    ws.column_dimensions["A"].width = 46
    for col in "BCDE":
        ws.column_dimensions[col].width = 17
    ws.column_dimensions["F"].width = 60
    periods = sorted({(r["dateFrom"], r["dateTo"]) for r in rows})
    ws["A1"] = "Сравнение FBS и FBO по финансовым отчётам Wildberries"
    ws["A1"].font = Font(name=FONT, bold=True, size=14)
    ws["A2"] = (f"Период отчётов: {periods[0][0]} — {max(p[1] for p in periods)} · "
                f"отчётов: {len({r['reportId'] for r in rows})} · строк детализации: {len(rows)}")
    ws["A2"].font = Font(name=FONT, size=10, color="595959")
    hdr = ["Показатель", "FBO", "FBS", "Не зависит от формата", "Всего", "Пояснение"]
    for i, h in enumerate(hdr, 1):
        ws.cell(row=4, column=i, value=h)
    style_header(ws, 4, 6, 30)
    # ключи форматов, на которые ссылаются формулы
    ws["B4"], ws["C4"], ws["D4"] = "FBO", "FBS", "—"
    ws["D4"].comment = Comment("Колонка «—»: строки без привязки к формату "
                               "(WB Продвижение, часть возмещений и т.п.).", "Отчёт")

    lines = []  # (label, kind, formula-template using {c} for column letter, fmt, note, total)

    def add(label, tpl, fmt, note="", total="sum", section=False, key=False):
        lines.append((label, tpl, fmt, note, total, section, key))

    add("Продажи", None, None, section=True)
    add("Продажи, шт", lambda c: "=" + sumf("sales", f"{c}$4"), QTY, "Строки «Продажа»")
    add("Возвраты, шт", lambda c: "=" + sumf("rets", f"{c}$4"), QTY, "Строки «Возврат»")
    add("Продано нетто, шт", lambda c: "={c}{r1}-{c}{r2}", QTY, "Продажи − возвраты")
    add("Доля продаж (шт)", lambda c: "=IFERROR({c}{r1}/($B{r1}+$C{r1}),0)", PCT, "От продаж FBO+FBS", total=None)
    add("Выручка (цена продавца со скидкой)", lambda c: "=" + sumf("rev", f"{c}$4"), RUB,
        "Продажи − возвраты, поле retailPriceWithDisc")
    add("Оплатил покупатель", lambda c: "=" + sumf("paid", f"{c}$4"), RUB, "После СПП, поле retailAmount")
    add("Средняя цена продажи", lambda c: "=IFERROR({c}{rev}/{c}{net_qty},0)", RUB, "Выручка / продано нетто", total="ratio")
    add("Комиссия", None, None, section=True)
    add("Тарифная комиссия (средневзвешенная)", lambda c: "=IFERROR(" + sumf("tariffw", f"{c}$4") + "/{c}{rev}/100,0)", PCT,
        "Тариф WB из отчёта, взвешенный по выручке", total="tariff")
    add("К перечислению за товар", lambda c: "=" + sumf("forpay", f"{c}$4"), RUB, "Поле forPay по продажам и возвратам")
    add("Комиссия WB + эквайринг, ₽", lambda c: "={c}{rev}-{c}{forpay}", RUB, "Выручка − к перечислению", key=True)
    add("Комиссия WB + эквайринг, % выручки", lambda c: "=IFERROR({c}{comm}/{c}{rev},0)", PCT, "Итоговая комиссия", total="ratio", key=True)
    add("   в т.ч. эквайринг", lambda c: "=" + sumf("acq", f"{c}$4"), RUB, "")
    add("Расходы WB сверх комиссии", None, None, section=True)
    add("Логистика", lambda c: "=" + sumf("logi", f"{c}$4"), RUB, "Доставка до покупателя и возвраты")
    add("Логистика на 1 продажу", lambda c: "=IFERROR({c}{logi}/{c}{r1},0)", RUB, "", total="ratio")
    add("Возмещение издержек по перемещению", lambda c: "=" + sumf("rebill", f"{c}$4"), RUB, "")
    add("Возмещение за выдачу/возврат на ПВЗ", lambda c: "=" + sumf("pvz", f"{c}$4"), RUB, "")
    add("Штрафы", lambda c: "=" + sumf("pen", f"{c}$4"), RUB, "Подробно — лист «Штрафы»", key=True)
    add("Хранение", lambda c: "=" + sumf("stor", f"{c}$4"), RUB, "Только склады WB (FBO)")
    add("Приёмка", lambda c: "=" + sumf("accept", f"{c}$4"), RUB, "")
    add("Удержания (WB Продвижение и пр.)", lambda c: "=" + sumf("ded", f"{c}$4"), RUB, "Реклама — не зависит от формата")
    add("Лояльность: баллы и участие", lambda c: "=" + sumf("loy", f"{c}$4"), RUB, "")
    add("Расходы сверх комиссии, итого", lambda c: "=SUM({c}{logi}:{c}{loy})-{c}{logi_unit}", RUB, "")
    add("Итог", None, None, section=True)
    add("Прочие выплаты и доплаты", lambda c: "=" + sumf("otherpay", f"{c}$4") + "+" + sumf("addpay", f"{c}$4"), RUB,
        "Добровольные компенсации, корректировки эквайринга")
    add("Компенсация скидки лояльности", lambda c: "=" + sumf("loycomp", f"{c}$4"), RUB, "Доход продавца")
    add("Все удержания WB, % выручки", lambda c: "=IFERROR(({c}{comm}+{c}{exp})/{c}{rev},0)", PCT, "Комиссия + расходы", total="ratio")
    add("Итого к получению", lambda c: "={c}{forpay}+{c}{other}+{c}{loycomp}-{c}{exp}", RUB, "Без вашей себестоимости и своих расходов", key=True)
    add("Итого к получению, % выручки", lambda c: "=IFERROR({c}{netv}/{c}{rev},0)", PCT, "", total="ratio", key=True)
    add("Итого без штрафов, % выручки", lambda c: "=IFERROR(({c}{netv}+{c}{pen})/{c}{rev},0)", PCT,
        "Сколько оставалось бы без штрафов", total="ratio")
    add("Итого на 1 проданную шт", lambda c: "=IFERROR({c}{netv}/{c}{net_qty},0)", RUB, "", total="ratio", key=True)

    # раскладка строк
    names = {"Продажи, шт": "r1", "Возвраты, шт": "r2", "Продано нетто, шт": "net_qty",
             "Выручка (цена продавца со скидкой)": "rev", "К перечислению за товар": "forpay",
             "Комиссия WB + эквайринг, ₽": "comm", "Логистика": "logi", "Логистика на 1 продажу": "logi_unit",
             "Штрафы": "pen", "Лояльность: баллы и участие": "loy", "Расходы сверх комиссии, итого": "exp",
             "Прочие выплаты и доплаты": "other", "Компенсация скидки лояльности": "loycomp",
             "Итого к получению": "netv"}
    pos, r = {}, 5
    for ln in lines:
        if ln[0] in names:
            pos[names[ln[0]]] = r
        r += 1
    r = 5
    for label, tpl, fmt, note, total, section, key in lines:
        if section:
            ws.cell(row=r, column=1, value=label)
            for c in range(1, 7):
                x = ws.cell(row=r, column=c)
                x.fill, x.font, x.border = SUB_FILL, Font(name=FONT, bold=True, size=10), BOX
            r += 1
            continue
        fill = KEY_FILL if key else None
        cell(ws, f"A{r}", label, bold=key, fill=fill)
        for c in "BCD":
            cell(ws, f"{c}{r}", tpl(c).format(c=c, **pos), fmt, bold=key, fill=fill)
        if total == "sum":
            tf = f"=SUM(B{r}:D{r})"
        elif total == "ratio":
            tf = tpl("E").format(c="E", **pos)
        elif total == "tariff":
            tf = f"=IFERROR(SUM({rng('tariffw')})/E{pos['rev']}/100,0)"
        else:
            tf = None
        cell(ws, f"E{r}", tf, fmt, bold=key, fill=fill)
        cell(ws, f"F{r}", note, color="595959")
        r += 1
    # блок «одни и те же артикулы»
    r += 1
    ws.cell(row=r, column=1, value="Одни и те же артикулы в обоих форматах")
    ws.cell(row=r, column=1).font = Font(name=FONT, bold=True, size=12)
    r += 1
    for i, h in enumerate(["Показатель", "FBO", "FBS"], 1):
        ws.cell(row=r, column=i, value=h)
    style_header(ws, r, 3, 22)
    sk = "'По артикулам'!"
    n_sku = len({x.get("nmId") for x in rows if x.get("nmId")})
    sk_last = 4 + n_sku
    both = f"({sk}$C$5:$C${sk_last}>0)*({sk}$D$5:$D${sk_last}>0)"
    r += 1
    cell(ws, f"A{r}", "Кол-во артикулов, продававшихся в обоих форматах")
    cell(ws, f"B{r}", f"=SUMPRODUCT({both})", QTY)
    cell(ws, f"C{r}", f"=B{r}", QTY)
    r += 1
    cell(ws, f"A{r}", "Продано нетто, шт")
    cell(ws, f"B{r}", f"=SUMPRODUCT({both}*{sk}$C$5:$C${sk_last})", QTY)
    cell(ws, f"C{r}", f"=SUMPRODUCT({both}*{sk}$D$5:$D${sk_last})", QTY)
    r += 1
    cell(ws, f"A{r}", "Средняя цена")
    cell(ws, f"B{r}", f"=IFERROR(SUMPRODUCT({both}*{sk}$E$5:$E${sk_last})/B{r-1},0)", RUB)
    cell(ws, f"C{r}", f"=IFERROR(SUMPRODUCT({both}*{sk}$F$5:$F${sk_last})/C{r-1},0)", RUB)
    r += 1
    cell(ws, f"A{r}", "Комиссия WB + эквайринг, % выручки", bold=True, fill=KEY_FILL)
    cell(ws, f"B{r}", f"=IFERROR(1-SUMPRODUCT({both}*{sk}$G$5:$G${sk_last})/SUMPRODUCT({both}*{sk}$E$5:$E${sk_last}),0)", PCT, bold=True, fill=KEY_FILL)
    cell(ws, f"C{r}", f"=IFERROR(1-SUMPRODUCT({both}*{sk}$H$5:$H${sk_last})/SUMPRODUCT({both}*{sk}$F$5:$F${sk_last}),0)", PCT, bold=True, fill=KEY_FILL)
    r += 2
    ws.cell(row=r, column=1, value="Вывод").font = Font(name=FONT, bold=True, size=12)
    concl = [
        "• FBO сейчас выгоднее: «Итого к получению, % выручки» и «на 1 шт» заметно выше, чем у FBS.",
        "• Комиссия WB у форматов почти одинаковая (FBS дороже примерно на 1 п.п.), логистика на продажу — одинаковая.",
        "• Разницу создают штрафы FBS «за нарушение срока передачи товара»: без штрафов форматы почти равны.",
        "• В отчёте WB нет ваших собственных расходов: склад и доставка до WB для FBS, поставки на склады WB для FBO.",
    ]
    for t in concl:
        r += 1
        ws.cell(row=r, column=1, value=t).font = Font(name=FONT, size=10)
    ws.freeze_panes = "B5"

    # ---------- Штрафы ----------
    ws = ws_pen
    reasons = sorted({x.get("bonusTypeName") or "(без основания)" for x in rows if x.get("sellerOperName") == "Штраф"},
                     key=lambda s: -sum(f(x.get("penalty")) for x in rows
                                         if x.get("sellerOperName") == "Штраф" and (x.get("bonusTypeName") or "(без основания)") == s))
    ws["A1"] = "Штрафы по основаниям и форматам"
    ws["A1"].font = Font(name=FONT, bold=True, size=14)
    hdr = ["Основание", "FBO, ₽", "FBS, ₽", "Не определено, ₽", "Всего, ₽", "FBO, строк", "FBS, строк", "Не опр., строк"]
    for i, h in enumerate(hdr, 1):
        ws.cell(row=3, column=i, value=h)
    style_header(ws, 3, len(hdr), 30)
    ws.column_dimensions["A"].width = 70
    for col in "BCDEFGH":
        ws.column_dimensions[col].width = 14
    op_cond = f"{rng('op')},\"Штраф\""
    for i, reason in enumerate(reasons, 4):
        cell(ws, f"A{i}", reason, wrap=True)
        crit = f"$A{i}" if reason != "(без основания)" else '""'
        for col, fk in zip("BCD", ("\"FBO\"", "\"FBS\"", "\"—\"")):
            cell(ws, f"{col}{i}", f"=SUMIFS({rng('pen')},{rng('fmt')},{fk},{rng('reason')},{crit},{op_cond})", RUB)
        cell(ws, f"E{i}", f"=SUM(B{i}:D{i})", RUB, bold=True)
        for col, fk in zip("FGH", ("\"FBO\"", "\"FBS\"", "\"—\"")):
            cell(ws, f"{col}{i}", f"=COUNTIFS({rng('fmt')},{fk},{rng('reason')},{crit},{op_cond})", QTY)
    t = 4 + len(reasons)
    cell(ws, f"A{t}", "Итого", bold=True, fill=SUB_FILL)
    for col in "BCDEFGH":
        cell(ws, f"{col}{t}", f"=SUM({col}4:{col}{t-1})", RUB if col in "BCDE" else QTY, bold=True, fill=SUB_FILL)
    cell(ws, f"A{t+1}", "Штрафы, % выручки формата")
    cell(ws, f"B{t+1}", f"=IFERROR(B{t}/Сводка!B{pos['rev']},0)", PCT)
    cell(ws, f"C{t+1}", f"=IFERROR(C{t}/Сводка!C{pos['rev']},0)", PCT)
    ws[f"A{t+3}"] = "Отрицательные суммы — сторно (возврат ранее начисленного штрафа)."
    ws[f"A{t+3}"].font = Font(name=FONT, size=9, color="595959")
    ws.freeze_panes = "B4"

    # ---------- По артикулам ----------
    ws = ws_sku
    ws["A1"] = "Продажи и комиссия по артикулам: FBO vs FBS"
    ws["A1"].font = Font(name=FONT, bold=True, size=14)
    ws["A2"] = "Нетто = продажи − возвраты. Комиссия = 1 − к перечислению / выручка."
    ws["A2"].font = Font(name=FONT, size=9, color="595959")
    hdr = ["Артикул WB (nmId)", "Артикул продавца", "FBO, шт нетто", "FBS, шт нетто", "FBO выручка", "FBS выручка",
           "FBO к перечислению", "FBS к перечислению", "FBO комиссия, %", "FBS комиссия, %", "Доля FBS (шт)", "Предмет"]
    for i, h in enumerate(hdr, 1):
        ws.cell(row=4, column=i, value=h)
    style_header(ws, 4, len(hdr), 32)
    widths = [14, 26, 11, 11, 14, 14, 14, 14, 11, 11, 11, 16]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    rev_by = defaultdict(float)
    label = {}
    for x in rows:
        nm = x.get("nmId")
        if nm:
            rev_by[nm] += _signed(x, "retailPriceWithDisc")
            label.setdefault(nm, (x.get("vendorCode"), x.get("subjectName")))
    nms = sorted({x.get("nmId") for x in rows if x.get("nmId")}, key=lambda n: -rev_by[n])
    for i, nm in enumerate(nms, 5):
        cell(ws, f"A{i}", nm, "0")
        cell(ws, f"B{i}", label[nm][0])
        for col, key, fk in (("C", "sales", '"FBO"'), ("D", "sales", '"FBS"'), ("E", "rev", '"FBO"'),
                             ("F", "rev", '"FBS"'), ("G", "forpay", '"FBO"'), ("H", "forpay", '"FBS"')):
            if key == "sales":
                fml = (f"=SUMIFS({rng('sales')},{rng('fmt')},{fk},{rng('nm')},$A{i})"
                       f"-SUMIFS({rng('rets')},{rng('fmt')},{fk},{rng('nm')},$A{i})")
            else:
                fml = f"=SUMIFS({rng(key)},{rng('fmt')},{fk},{rng('nm')},$A{i})"
            cell(ws, f"{col}{i}", fml, QTY if key == "sales" else RUB)
        cell(ws, f"I{i}", f'=IF(E{i}<>0,1-G{i}/E{i},"")', PCT)
        cell(ws, f"J{i}", f'=IF(F{i}<>0,1-H{i}/F{i},"")', PCT)
        cell(ws, f"K{i}", f'=IF((C{i}+D{i})<>0,D{i}/(C{i}+D{i}),"")', PCT)
        cell(ws, f"L{i}", label[nm][1])
    t = 5 + len(nms)
    cell(ws, f"A{t}", "Итого", bold=True, fill=SUB_FILL)
    cell(ws, f"B{t}", None, fill=SUB_FILL)
    for col in "CDEFGH":
        cell(ws, f"{col}{t}", f"=SUM({col}5:{col}{t-1})", QTY if col in "CD" else RUB, bold=True, fill=SUB_FILL)
    cell(ws, f"I{t}", f'=IF(E{t}<>0,1-G{t}/E{t},"")', PCT, bold=True, fill=SUB_FILL)
    cell(ws, f"J{t}", f'=IF(F{t}<>0,1-H{t}/F{t},"")', PCT, bold=True, fill=SUB_FILL)
    cell(ws, f"K{t}", f'=IF((C{t}+D{t})<>0,D{t}/(C{t}+D{t}),"")', PCT, bold=True, fill=SUB_FILL)
    cell(ws, f"L{t}", None, fill=SUB_FILL)
    ws.freeze_panes = "C5"
    ws.auto_filter.ref = f"A4:L{t-1}"

    # ---------- Отчёты ----------
    ws = ws_rep
    ws["A1"] = "Финансовые отчёты, вошедшие в расчёт"
    ws["A1"].font = Font(name=FONT, bold=True, size=14)
    hdr = ["Отчёт №", "Период с", "Период по", "Тип отчёта", "Строк", "Продажи, шт", "Выручка", "К перечислению за товар"]
    for i, h in enumerate(hdr, 1):
        ws.cell(row=3, column=i, value=h)
    style_header(ws, 3, len(hdr), 30)
    for i, w in enumerate([14, 12, 12, 12, 10, 12, 16, 18], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    reps = sorted({(x["reportId"], x["dateFrom"], x["dateTo"], x.get("reportType")) for x in rows},
                  key=lambda t: (t[1], t[3], t[0]))
    for i, (rid, d1, d2, rt) in enumerate(reps, 4):
        cell(ws, f"A{i}", rid, "0")
        cell(ws, f"B{i}", d1)
        cell(ws, f"C{i}", d2)
        cell(ws, f"D{i}", {1: "Основной", 2: "Тип 2 (продажи в СНГ)"}.get(rt, rt))
        cell(ws, f"E{i}", f"=COUNTIFS({rng('report')},$A{i})", QTY)
        cell(ws, f"F{i}", f"=SUMIFS({rng('sales')},{rng('report')},$A{i})", QTY)
        cell(ws, f"G{i}", f"=SUMIFS({rng('rev')},{rng('report')},$A{i})", RUB)
        cell(ws, f"H{i}", f"=SUMIFS({rng('forpay')},{rng('report')},$A{i})", RUB)
    ws[f"D{4}"].comment = Comment("reportType из API: 1 — основной отчёт, 2 — отдельный отчёт "
                                  "(в данных — продажи в Беларусь, Казахстан, Армению и др.).", "Отчёт")
    t = 4 + len(reps)
    cell(ws, f"A{t}", "Итого", bold=True, fill=SUB_FILL)
    for col in "BCD":
        cell(ws, f"{col}{t}", None, fill=SUB_FILL)
    for col in "EFGH":
        cell(ws, f"{col}{t}", f"=SUM({col}4:{col}{t-1})", QTY if col in "EF" else RUB, bold=True, fill=SUB_FILL)

    # ---------- Методика ----------
    ws = ws_m
    ws.column_dimensions["A"].width = 120
    text = [
        ("Источник и методика", True),
        ("Данные: API Wildberries, POST https://finance-api.wildberries.ru/api/finance/v1/sales-reports/detailed "
         "(детализация еженедельных финансовых отчётов; старый метод v5 reportDetailByPeriod отключён).", False),
        (f"Период отчётов: {periods[0][0]} — {max(p[1] for p in periods)}. Выгрузка сформирована скриптом wb_fbs_fbo_excel.py.", False),
        ("", False),
        ("Как определяется формат (колонка «Формат» в «Детализации»)", True),
        ("1. Строки логистики содержат способ доставки WB: «FBW…» → FBO, «FBS…» → FBS.", False),
        ("2. У продаж, возвратов и прочих строк способа доставки нет — формат берётся по srid (идентификатор заказа) "
         "из строк логистики того же заказа.", False),
        ("3. Если заказа нет в логистике: склад «Склад поставщика…» → FBS; затем поиск по shkId (штрихкод экземпляра).", False),
        ("4. Если и это не помогло — по смыслу операции: хранение и расхождения при приёмке на складе WB → FBO; "
         "штрафы «за нарушение срока передачи товара» и «Штраф МП» (невыполненные заказы) → FBS.", False),
        ("5. Удержания («WB Продвижение» и т.п.) не зависят от формата — «—».", False),
        ("Результат: все продажи и возвраты привязаны к формату; без привязки остаются только удержания и мелкие возмещения.", False),
        ("", False),
        ("Формулы показателей", True),
        ("Выручка = цена продавца со скидкой (retailPriceWithDisc) по продажам минус возвраты.", False),
        ("Комиссия WB + эквайринг = выручка − «к перечислению за товар» (forPay). Включает комиссию по тарифу, "
         "эквайринг и вознаграждение ПВЗ.", False),
        ("Расходы сверх комиссии = логистика + возмещение издержек по перемещению + возмещение ПВЗ + штрафы + хранение "
         "+ приёмка + удержания + баллы лояльности.", False),
        ("Итого к получению = к перечислению за товар + прочие выплаты и доплаты + компенсация скидки лояльности − расходы сверх комиссии.", False),
        ("По возвратам суммы берутся со знаком минус (в «Детализации» уже со знаком, как они входят в расчёт).", False),
        ("", False),
        ("Что не учтено", True),
        ("Себестоимость товара, налоги, собственные расходы продавца: свой склад и доставка до WB (FBS), "
         "доставка поставок на склады WB (FBO).", False),
    ]
    for i, (t, b) in enumerate(text, 1):
        c = ws.cell(row=i, column=1, value=t)
        c.font = Font(name=FONT, bold=b, size=12 if b else 10)
        c.alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(out)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("date_from", nargs="?")
    p.add_argument("date_to", nargs="?")
    p.add_argument("--file")
    p.add_argument("-o", "--out", default="wb_fbs_vs_fbo.xlsx")
    a = p.parse_args()
    if a.file:
        paths = [a.file] if os.path.isfile(a.file) else sorted(
            os.path.join(a.file, x) for x in os.listdir(a.file) if x.endswith(".json"))
        rows = []
        for path in paths:
            with open(path, encoding="utf-8") as fh:
                rows += json.load(fh)
    else:
        token = os.environ.get("WB_API_TOKEN")
        if not token or not (a.date_from and a.date_to):
            sys.exit("Нужны WB_API_TOKEN и даты: wb_fbs_fbo_excel.py YYYY-MM-DD YYYY-MM-DD")
        rows = fetch(a.date_from, a.date_to, token)
    if not rows:
        sys.exit("За период нет строк отчёта")
    print(build(rows, a.out))


if __name__ == "__main__":
    main()
