#!/usr/bin/env python3
"""
lab-setup.py — يهيّئ حالة المستودع لمختبر معيّن.

الغرض: ألا يتعثّر أي متدرّب في بناء «الحالة» بدل التدرّب على Git نفسه.
المدرّب (أو المتدرّب) ينفّذ الأمر فيجد المستودع في الحالة المطلوبة تماماً.

    python lab-setup.py list          # اعرض المختبرات المدعومة
    python lab-setup.py 11            # هيّئ حالة المختبر 11
    python lab-setup.py 11 --dry-run  # اعرض الأوامر دون تنفيذها

ملاحظة: يعمل على ويندوز وماك ولينكس — يستدعي git عبر subprocess فقط.
"""

import argparse
import subprocess
import sys
import os

DRY = False


def run(*args, check=True):
    cmd = list(args)
    if DRY:
        print("   $ " + " ".join(cmd))
        return ""
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"   ! فشل: {' '.join(cmd)}\n     {r.stderr.strip()}", file=sys.stderr)
    return r.stdout.strip()


def write(path, text):
    if DRY:
        print(f"   > اكتب {path}")
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def append(path, text):
    if DRY:
        print(f"   >> أضف إلى {path}")
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


def commit(msg):
    run("git", "add", "-A")
    run("git", "commit", "-m", msg, "--no-verify")


def ensure_repo():
    if not os.path.isdir(".git"):
        print("   • تهيئة مستودع جديد")
        run("git", "init", "-b", "main")
    if not run("git", "log", "-1", "--oneline", check=False):
        commit("chore: initialize project structure")


# ═════════════════════════ المختبرات ═════════════════════════

def lab_07():
    """مختبر 7 — فرع الميزة جاهز للإنشاء (main نظيف وملتزم)."""
    ensure_repo()
    run("git", "switch", "main", check=False)
    print("   ✔ main نظيف. نفّذ الآن:  git switch -c feature/missing-values")


def lab_09():
    """مختبر 9 — فرع feat/column-normalizer فيه تغيير جاهز لفتح PR."""
    ensure_repo()
    run("git", "switch", "main", check=False)
    run("git", "switch", "-c", "feat/column-normalizer", check=False)
    append("clean.py", '\n\ndef preview_columns(header):\n'
                       '    """يطبع أسماء الأعمدة قبل وبعد التوحيد — مفيد للمراجعة."""\n'
                       '    for old, new in zip(header, normalize_columns(header)):\n'
                       '        print(f"{old!r:28} -> {new!r}")\n')
    commit("feat: add column preview helper")
    print("   ✔ الفرع feat/column-normalizer جاهز. ارفعه ثم افتح Pull Request.")


def lab_11():
    """مختبر 11 — خمس commits فوضوية جاهزة للتنظيف بـ rebase -i."""
    ensure_repo()
    run("git", "switch", "main", check=False)
    run("git", "branch", "-D", "exp/cleanup-demo", check=False)
    run("git", "switch", "-c", "exp/cleanup-demo")
    steps = [
        ("docs/eval.md", "# تقرير التقييم\n", "feat: add eval report skeleton"),
        ("docs/eval.md", "\nعدد الصفوف قبل وبعد التنظيف.\n", "wip"),
        ("docs/eval.md", "\nنسبة القيم المفقودة لكل عمود.\n", "typo"),
        ("docs/eval.md", "\nعدد الصفوف المكررة المحذوفة.\n", "fix"),
        ("docs/summary.md", "# ملخص التشغيل\n", "feat: add run summary"),
    ]
    for path, text, msg in steps:
        append(path, text) if os.path.exists(path) else write(path, text)
        commit(msg)
    print("   ✔ خمس commits فوضوية جاهزة. نفّذ الآن:  git rebase -i HEAD~5")
    print("     اجعل 2 و3 و4 = fixup، والأولى = reword.")


def lab_12():
    """مختبر 12 — فرع تجريبي فيه عمل غير مكتمل + خطأ يحتاج إصلاحاً عاجلاً."""
    ensure_repo()
    run("git", "switch", "main", check=False)
    run("git", "branch", "-D", "exp/parallel-read", check=False)
    run("git", "switch", "-c", "exp/parallel-read")
    append("clean.py", "\n\n# TODO: قراءة متوازية للملفات الكبيرة — غير مكتملة\n")
    print("   ✔ تعديل غير ملتزم موجود الآن على exp/parallel-read.")
    print("     نفّذ:  git stash push -u -m \"نصف القراءة المتوازية\"")
    print("     ثم عالج الإصلاح العاجل على فرع fix/empty-file-crash.")


def lab_13():
    """مختبر 13 — يعيد main إلى نقطة مشتركة نظيفة قبل صناعة التعارض."""
    ensure_repo()
    run("git", "switch", "main", check=False)
    run("git", "branch", "-D", "fix/lr-tune", check=False)
    run("git", "branch", "-D", "exp/strategy-search", check=False)
    print("   ✔ الفرعان محذوفان و main نظيف — انطلقا معاً من هنا.")
    print("     أ:  git switch -c fix/strategy-tune   ثم غيّر missing_strategy إلى median")
    print("     ب:  git switch -c exp/strategy-search ثم غيّر نفس السطر إلى drop")


def lab_15():
    """مختبر 15 — يهيّئ ملفات الاختبار والتبعيات لتدفّق CI."""
    ensure_repo()
    print("   ✔ tests/test_clean.py و requirements.txt موجودان بالفعل.")
    print("     أنشئ الآن .github/workflows/ci.yml — انتبه للمسار حرفياً.")


LABS = {
    "7": lab_07, "9": lab_09, "11": lab_11,
    "12": lab_12, "13": lab_13, "15": lab_15,
}

DESC = {
    "7": "فرع الميزة — main نظيف وجاهز",
    "9": "فرع جاهز لفتح Pull Request ومراجعته",
    "11": "خمس commits فوضوية لتنظيفها بـ rebase -i",
    "12": "عمل غير مكتمل + سيناريو الإصلاح العاجل",
    "13": "إعادة الفروع إلى نقطة مشتركة لصناعة التعارض",
    "15": "التحقق من جاهزية ملفات CI",
}


def main():
    global DRY
    p = argparse.ArgumentParser(description="تهيئة حالة المستودع لمختبر معيّن")
    p.add_argument("lab", help="رقم المختبر، أو list لعرض القائمة")
    p.add_argument("--dry-run", action="store_true", help="اعرض الأوامر دون تنفيذها")
    a = p.parse_args()
    DRY = a.dry_run

    if a.lab == "list":
        print("المختبرات المدعومة:\n")
        for k in sorted(LABS, key=int):
            print(f"  {k:>2}  {DESC[k]}")
        print("\nالمختبرات 1–6 و8 و10 و14 لا تحتاج تهيئة — يبنيها المتدرّب بنفسه.")
        return

    fn = LABS.get(a.lab)
    if not fn:
        print(f"لا توجد تهيئة للمختبر {a.lab}. جرّب:  python lab-setup.py list")
        sys.exit(1)
    print(f"\n▶ تهيئة المختبر {a.lab} — {DESC[a.lab]}\n")
    fn()
    print()


if __name__ == "__main__":
    main()
