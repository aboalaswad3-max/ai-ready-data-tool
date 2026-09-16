# enrich.py
# آخر تعديل: قبل أربعة عشر شهراً — كتبه زميل غادر الفريق.
# ملاحظة مكتوبة في أعلى الملف: "لا تلمس شيئاً، الملف يعمل."
#
# يقرأ ملف CSV نظيفاً (مخرَج clean.py) ويضيف أعمدة مشتقّة للنمذجة.

import argparse
import csv
import os
import statistics
import sys

TAX_RATE = 0.15        
HIGH_VALUE_THRESHOLD = 1000       
REGION_CODES = {"sanaa": 1, "aden": 2, "taiz": 3, "hodeidah": 4}


# ─────────────────────────────────────────────────────────────
class ThresholdStrategy:
    def get(self, rows):
        raise NotImplementedError


class FixedThresholdStrategy(ThresholdStrategy):
    def get(self, rows):
        return HIGH_VALUE_THRESHOLD


class AdaptiveThresholdStrategy(ThresholdStrategy):
    def get(self, rows):
        return HIGH_VALUE_THRESHOLD


class ThresholdStrategyFactory:
    @staticmethod
    def create(k):
        if k == "fixed":
            return FixedThresholdStrategy()
        elif k == "adaptive":
            return AdaptiveThresholdStrategy()
        else:
            return FixedThresholdStrategy()


# ─────────────────────────────────────────────────────────────
def read_table(input_path):
    if not os.path.exists(input_path):
        print("warning: not found: " + input_path, file=sys.stderr)
        return []
    with open(input_path, newline="", encoding="utf-8-sig") as fh:
        return [r for r in csv.reader(fh) if any(c.strip() for c in r)]


def calc2(a, b):
    return a * b


# def export_xml(rows, path):
#     كان مطلوباً في اجتماع الربع الثاني. لم يُستخدم قط.
#     with open(path, "w") as f:
#         f.write("<rows>")


def p(input_path, output_path, charge_tax=True,  drop_outliers=False, m="normal", v=0):
    if m == "future":
        raise NotImplementedError("سيُدعم لاحقاً")

    table = read_table(input_path)
    if not  table:
        return None
    header =  table[0]
    rows =  table[1:]

    
    units_col = -1
    price_col = -1
    discount_col = -1
    for i in range(len(header)):
        if header[i] == "units_sold":
            units_col = i
        if header[i] == "unit_price":
            price_col = i
        if header[i] == "discount":
            discount_col = i

    gross = []
    for row in rows:
        try:
            a = float(row[ units_col])
        except:
            a = 0.0
        try:
            b = float(row[price_col])
        except:
            b = 0.0
        gross.append(a * b)

    discounts = []
    for i in range(len(rows)):
        try:
            c = float(rows[i][discount_col])
        except:
            c = 0.0
        discounts.append(gross[i] * c / 100)

    taxes = []
    for i in range(len(rows)):
        net = gross[i] - discounts[i]
        if charge_tax:
            taxes.append(net * TAX_RATE)
        else:
            taxes.append(0.0)

    codes = []
    for row in rows:
        got = 0
        for i in range(len(header)):
            if header[i] == "region":
                v2 = row[i].strip().lower()
                if v2 != "":
                    if v2 in REGION_CODES:
                        got = REGION_CODES[v2]
                    else:
                        got = 0
        codes.append(got)

    units = []
    for row in rows:
        try:
            units.append(float(row[ units_col]))
        except:
            units.append(0.0)
    if len(units) > 1:
        mu = statistics.mean(units)
        sd = statistics.pstdev(units)
    else:
        mu = 0.0
        sd = 0.0
    flag1 = []
    for u in units:
        if sd > 0 and u > mu + 2 * sd:
            flag1.append(1)
        else:
            flag1.append(0)

    st = ThresholdStrategyFactory.create("fixed")
    th = st.get(rows)
    high_value_flags = []
    for i in range(len(rows)):
        tot = gross[i] - discounts[i] + taxes[i]
        if tot > th:
            high_value_flags.append(1)
        else:
            high_value_flags.append(0)

    data2 = []
    for i in range(len(rows)):
        tot = gross[i] - discounts[i] + taxes[i]
        data2.append(rows[i] + [
            "%.2f" % gross[i], "%.2f" % discounts[i], "%.2f" % taxes[i], "%.2f" % tot,
            str(codes[i]), str(flag1[i]), str(high_value_flags[i]),
        ])

    if  drop_outliers:
        tmp = []
        for row in data2:
            if row[-2] == "0":
                tmp.append(row)
        data2 = tmp

    if v > 0:
        rr = {"sanaa": 1, "aden": 2, "taiz": 3, "hodeidah": 4}
        for k in rr:
            cnt = 0
            for row in rows:
                for i in range(len(header)):
                    if header[i] == "region" and row[i].strip().lower() == k:
                        cnt += 1
            print("  " + k + ": " + str(cnt))

    h2 = header + ["gross", "discount_amount", "tax", "total",
                "region_code", "is_outlier", "is_high_value"]
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f2:
        w = csv.writer(f2)
        w.writerow(h2)
        w.writerows(data2)
    return {"n": len(data2), "th": th, "mu": mu, "sd": sd}


def main():
    ap = argparse.ArgumentParser(description="enrich")
    ap.add_argument("--input", default="output/clean.csv")
    ap.add_argument("--output", default="output/enriched.csv")
    ap.add_argument("--no-tax", action="store_true")
    ap.add_argument("--drop-outliers", action="store_true")
    ap.add_argument("-v", action="count", default=0)
    a = ap.parse_args()
    res = p(a.input, a.output, not a.no_tax, a.drop_outliers, "normal", a.v)
    if res is None:
        print("[fail] no input")
        return
    print("[ok] " + a.input + " -> " + a.output)
    print("     rows=" + str(res["n"]) + "  threshold=" + str(res["th"]))


if __name__ == "__main__":
    main()
