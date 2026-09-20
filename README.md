# File Integrity Checker

A small, auditable, local-first Python tool for creating **SHA-256 integrity baselines** and detecting added, modified, or missing files later. It is useful for release folders, backups, configuration directories, static sites, research data, and any directory where unexpected changes matter.

> No cloud service, account, API key, telemetry, or network access is required.

## English

### Why it exists
File timestamps and sizes alone cannot reliably prove that content is unchanged. File Integrity Checker records a cryptographic SHA-256 digest for each tracked file, then recomputes digests during verification and reports exact differences.

### Features
- Recursive SHA-256 baseline generation.
- Detects **added**, **modified**, and **missing** files.
- Verifies a copied directory with `--root`.
- Hidden files are excluded by default and can be opted in.
- Symbolic links are never followed, reducing traversal surprises.
- Atomic baseline writes and overwrite protection.
- Deterministic, portable JSON baseline format.
- Human-readable output plus JSON reports for automation.
- Meaningful exit codes: `0` clean, `1` integrity changes, `2` operational/input error.
- Python API and dependency-light CLI (runtime uses the standard library only).

### Preview
```text
$ file-integrity check integrity-baseline.json
MODIFIED config/app.ini
MISSING  assets/logo.svg
ADDED    notes.txt
Changes: 3 (added=1, modified=1, missing=1)
```
This text preview is representative of the implemented CLI. No graphical UI is included.

### Requirements & installation
- Python 3.10+

```bash
git clone https://github.com/rad03i2/file-integrity-checker.git
cd file-integrity-checker
python -m pip install -e .
```

### Usage
Create a baseline:
```bash
file-integrity init ./important-files -o baseline.json
```
Verify later:
```bash
file-integrity check baseline.json
```
Verify another copy of the same tree:
```bash
file-integrity check baseline.json --root ./restored-copy
```
Machine-readable report:
```bash
file-integrity check baseline.json --json
```
Track dotfiles too:
```bash
file-integrity init ./important-files -o baseline.json --include-hidden
```
Use `--overwrite` only when intentionally replacing an existing baseline.

### Python API
```python
from pathlib import Path
from file_integrity_checker import build_baseline, verify

baseline = build_baseline(Path("important-files"))
changes = verify(baseline, Path("important-files"))
```

### Configuration
There is deliberately no config file or environment-variable requirement. Behavior is explicit through CLI flags. Baselines contain the schema version, creation time, original root, algorithm, relative paths, sizes, modification timestamps, and SHA-256 digests.

### Project structure
```text
src/file_integrity_checker/  core engine, CLI and public API
tests/                       engine and CLI tests
.github/workflows/ci.yml     cross-platform CI
pyproject.toml               packaging/tool configuration
```

### Testing
```bash
python -m pip install -e . pytest ruff
ruff check src tests
pytest -q
```
CI runs linting and tests on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13.

### Security & privacy
All hashing is local. The tool does **not** modify tracked files. Treat a baseline as security-relevant metadata: if an attacker can replace both files and their baseline, verification cannot establish trust. Store trusted baselines separately or protect them with appropriate access controls. SHA-256 detects content differences; it does not identify who changed a file or whether a changed file is malicious.

### Limitations
- File contents are read in full (streamed in chunks), so large trees can take time and disk I/O.
- Permissions, ownership, ACLs, extended attributes, and directory metadata are not integrity-checked.
- Symbolic links are intentionally excluded.
- This is integrity monitoring, not malware detection, backup software, or digital signing.

### Optional roadmap
Potential future work includes signed baselines and opt-in metadata/permission checks. These are not current features.

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Security guidance is in [SECURITY.md](SECURITY.md).

### License
MIT — see [LICENSE](LICENSE).

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

## العربية

### نظرة عامة
**File Integrity Checker** أداة بايثون محلية لإنشاء خط أساس لسلامة الملفات باستخدام **SHA-256** ثم اكتشاف الملفات المضافة أو المعدلة أو المفقودة لاحقًا. تناسب مجلدات الإصدارات والنسخ الاحتياطية والإعدادات والمواقع الثابتة والبيانات التي يهم التأكد من عدم تغيرها.

لا تحتاج الأداة إلى خدمة سحابية أو حساب أو مفتاح API أو اتصال بالإنترنت.

### لماذا هذا المشروع؟
الحجم وتاريخ التعديل لا يكفيان لإثبات أن محتوى الملف لم يتغير. تسجل الأداة بصمة SHA-256 مشفرة لكل ملف، ثم تعيد حسابها عند الفحص وتقارن النتيجة بخط الأساس الموثوق.

### المميزات
- إنشاء خط أساس SHA-256 للمجلدات بشكل متكرر.
- اكتشاف الملفات **المضافة والمعدلة والمفقودة**.
- فحص نسخة أخرى من المجلد باستخدام `--root`.
- تجاهل الملفات المخفية افتراضيًا مع إمكانية تضمينها.
- عدم تتبع الروابط الرمزية لسلامة اجتياز المسارات.
- كتابة ذرية لملف خط الأساس ومنع الاستبدال العرضي.
- صيغة JSON واضحة وقابلة للنقل.
- مخرجات بشرية أو JSON للأتمتة.
- رموز خروج مفيدة: `0` سليم، `1` تغييرات، `2` خطأ إدخال/تشغيل.
- واجهة Python بالإضافة إلى CLI، ولا توجد تبعيات تشغيل خارج المكتبة القياسية.

### التثبيت
يتطلب Python 3.10 أو أحدث:
```bash
git clone https://github.com/rad03i2/file-integrity-checker.git
cd file-integrity-checker
python -m pip install -e .
```

### الاستخدام
إنشاء خط أساس:
```bash
file-integrity init ./important-files -o baseline.json
```
الفحص لاحقًا:
```bash
file-integrity check baseline.json
```
فحص نسخة مستعادة:
```bash
file-integrity check baseline.json --root ./restored-copy
```
تقرير JSON:
```bash
file-integrity check baseline.json --json
```
لتضمين الملفات المخفية استخدم `--include-hidden`. ولا تستخدم `--overwrite` إلا عند قصد استبدال خط أساس موجود.

### الإعدادات
لا يوجد ملف إعدادات أو متغيرات بيئة مطلوبة عمدًا؛ كل السلوكيات المهمة صريحة عبر خيارات CLI. يحفظ خط الأساس نسخة المخطط ووقت الإنشاء والجذر الأصلي والخوارزمية والمسارات النسبية والأحجام وأوقات التعديل وبصمات SHA-256.

### بنية المشروع
`src/file_integrity_checker/` للمحرك وCLI وواجهة Python، و`tests/` للاختبارات، و`.github/workflows/ci.yml` للتكامل المستمر، و`pyproject.toml` للحزمة والأدوات.

### الاختبارات
```bash
python -m pip install -e . pytest ruff
ruff check src tests
pytest -q
```
يختبر CI المشروع على Ubuntu وWindows وmacOS مع Python 3.10 و3.12 و3.13.

### الأمان والخصوصية
تتم كل عمليات التجزئة محليًا، والأداة لا تعدل الملفات التي تفحصها. يجب حماية ملف خط الأساس أو حفظه في مكان موثوق؛ فإذا استطاع مهاجم تغيير الملفات وخط الأساس معًا فلن تكون المقارنة مصدر ثقة مستقل. SHA-256 يكشف اختلاف المحتوى لكنه لا يحدد من غيّره ولا يحكم إن كان الملف ضارًا.

### القيود
الأداة لا تتحقق من الصلاحيات والملكية وACL والسمات الممتدة وبيانات المجلدات، ولا تتبع الروابط الرمزية. فحص المجلدات الكبيرة يستهلك وقتًا وقراءة من القرص. المشروع أداة سلامة ملفات وليس مضاد فيروسات أو نظام نسخ احتياطي أو توقيعًا رقميًا.

### تطوير اختياري مستقبلًا
يمكن مستقبلًا إضافة توقيع خطوط الأساس أو فحص بيانات الصلاحيات بصورة اختيارية؛ هذه ليست ميزات حالية.

### المساهمة والترخيص
راجع [CONTRIBUTING.md](CONTRIBUTING.md) للمساهمة و[SECURITY.md](SECURITY.md) لإرشادات الأمان. المشروع مرخص وفق MIT في [LICENSE](LICENSE).

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
