# 00_data_overview.py

# 📌 إعدادات أساسية
from IPython import get_ipython
try:
    get_ipython().run_line_magic("pip", "install ipython")
except:
    pass  # يعمل فقط داخل Jupyter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from IPython.display import display
import importlib
import sys

# ⚙️ إعدادات العرض
pd.set_option('display.max_columns', 100)
sns.set(style="whitegrid")

# 📂 تحديد جذر المشروع وضبط sys.path
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]  # ✅ تصحيح المستوى
except NameError:
    PROJECT_ROOT = Path.cwd().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 📂 تحميل البيانات المنظفة
DATA_PATH = PROJECT_ROOT / "data_intelligence_system" / "data" / "processed" / "clean_data.csv"
print(f"مسار الملف المستخدم: {DATA_PATH}")
if not DATA_PATH.exists():
    raise FileNotFoundError(f"الملف غير موجود في المسار: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# ✅ عرض الشكل والمحتوى العام
print("✅ شكل البيانات:", df.shape)
display(df.head())

# 🔍 معلومات الأعمدة
print("\n🔍 معلومات الأعمدة:")
df.info()

# 📉 تحليل القيم المفقودة
print("\n📉 جدول القيم المفقودة:")
missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    "Missing Count": missing,
    "Missing %": missing_percent
})
missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values(by="Missing %", ascending=False)
display(missing_df)

# 📦 توزيع القيم الفريدة (Top 20)
print("\n📦 توزيع القيم الفريدة (Top 20):")
unique_counts = df.nunique().sort_values(ascending=False).head(20)
display(unique_counts)

# 🔢 إحصاءات عددية
print("\n🔢 الإحصاءات العددية:")
display(df.describe(include=[np.number]))

# 🎯 الأعمدة النوعية وتوزيعها (Top 5 فقط)
categorical_cols = df.select_dtypes(include='object').columns
for col in categorical_cols[:5]:
    print(f"\n🎯 العمود النوعي: {col}")
    print(df[col].value_counts().head(10))

    # رسم التوزيع
    plt.figure(figsize=(8, 4))
    sns.countplot(data=df, x=col, order=df[col].value_counts().index[:10])
    plt.title(f"Top 10 Values in '{col}'", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 📊 توزيع الأعمدة الرقمية (أول 5 فقط)
numeric_cols = df.select_dtypes(include=np.number).columns[:5]
df[numeric_cols].hist(figsize=(14, 10), bins=30, edgecolor='black')
plt.tight_layout()
plt.suptitle("📊 توزيعات أول 5 أعمدة رقمية", fontsize=16, y=1.02)
plt.show()

# 📘 تحديث سجل المصادر (اختياري من النوتبوك)
print("\n📘 تحديث سجل مصادر البيانات الخام (اختياري):")
try:
    register_module = importlib.import_module("data_intelligence_system.data.raw.register_sources")
    register_module.main()
    print("✅ تم تحديث سجل المصادر بنجاح.")
except Exception as e:
    print(f"❌ خطأ أثناء تحديث سجل المصادر: {e}")
# 00_data_overview.py

# 📌 إعدادات أساسية
from IPython import get_ipython
try:
    get_ipython().run_line_magic("pip", "install ipython")
except:
    pass  # يعمل فقط داخل Jupyter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from IPython.display import display
import importlib
import sys

# ⚙️ إعدادات العرض
pd.set_option('display.max_columns', 100)
sns.set(style="whitegrid")

# 📂 تحديد جذر المشروع وضبط sys.path
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]  # ✅ تصحيح المستوى
except NameError:
    PROJECT_ROOT = Path.cwd().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 📂 تحميل البيانات المنظفة
DATA_PATH = PROJECT_ROOT / "data_intelligence_system" / "data" / "processed" / "clean_data.csv"
print(f"مسار الملف المستخدم: {DATA_PATH}")
if not DATA_PATH.exists():
    raise FileNotFoundError(f"الملف غير موجود في المسار: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# ✅ عرض الشكل والمحتوى العام
print("✅ شكل البيانات:", df.shape)
display(df.head())

# 🔍 معلومات الأعمدة
print("\n🔍 معلومات الأعمدة:")
df.info()

# 📉 تحليل القيم المفقودة
print("\n📉 جدول القيم المفقودة:")
missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    "Missing Count": missing,
    "Missing %": missing_percent
})
missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values(by="Missing %", ascending=False)
display(missing_df)

# 📦 توزيع القيم الفريدة (Top 20)
print("\n📦 توزيع القيم الفريدة (Top 20):")
unique_counts = df.nunique().sort_values(ascending=False).head(20)
display(unique_counts)

# 🔢 إحصاءات عددية
print("\n🔢 الإحصاءات العددية:")
display(df.describe(include=[np.number]))

# 🎯 الأعمدة النوعية وتوزيعها (Top 5 فقط)
categorical_cols = df.select_dtypes(include='object').columns
for col in categorical_cols[:5]:
    print(f"\n🎯 العمود النوعي: {col}")
    print(df[col].value_counts().head(10))

    # رسم التوزيع
    plt.figure(figsize=(8, 4))
    sns.countplot(data=df, x=col, order=df[col].value_counts().index[:10])
    plt.title(f"Top 10 Values in '{col}'", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 📊 توزيع الأعمدة الرقمية (أول 5 فقط)
numeric_cols = df.select_dtypes(include=np.number).columns[:5]
df[numeric_cols].hist(figsize=(14, 10), bins=30, edgecolor='black')
plt.tight_layout()
plt.suptitle("📊 توزيعات أول 5 أعمدة رقمية", fontsize=16, y=1.02)
plt.show()

# 📘 تحديث سجل المصادر (اختياري من النوتبوك)
print("\n📘 تحديث سجل مصادر البيانات الخام (اختياري):")
try:
    register_module = importlib.import_module("data_intelligence_system.data.raw.register_sources")
    register_module.main()
    print("✅ تم تحديث سجل المصادر بنجاح.")
except Exception as e:
    print(f"❌ خطأ أثناء تحديث سجل المصادر: {e}")
# 00_data_overview.py

# 📌 إعدادات أساسية
from IPython import get_ipython
try:
    get_ipython().run_line_magic("pip", "install ipython")
except:
    pass  # يعمل فقط داخل Jupyter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from IPython.display import display
import importlib
import sys

# ⚙️ إعدادات العرض
pd.set_option('display.max_columns', 100)
sns.set(style="whitegrid")

# 📂 تحديد جذر المشروع وضبط sys.path
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]  # ✅ تصحيح المستوى
except NameError:
    PROJECT_ROOT = Path.cwd().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 📂 تحميل البيانات المنظفة
DATA_PATH = PROJECT_ROOT / "data_intelligence_system" / "data" / "processed" / "clean_data.csv"
print(f"مسار الملف المستخدم: {DATA_PATH}")
if not DATA_PATH.exists():
    raise FileNotFoundError(f"الملف غير موجود في المسار: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# ✅ عرض الشكل والمحتوى العام
print("✅ شكل البيانات:", df.shape)
display(df.head())

# 🔍 معلومات الأعمدة
print("\n🔍 معلومات الأعمدة:")
df.info()

# 📉 تحليل القيم المفقودة
print("\n📉 جدول القيم المفقودة:")
missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    "Missing Count": missing,
    "Missing %": missing_percent
})
missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values(by="Missing %", ascending=False)
display(missing_df)

# 📦 توزيع القيم الفريدة (Top 20)
print("\n📦 توزيع القيم الفريدة (Top 20):")
unique_counts = df.nunique().sort_values(ascending=False).head(20)
display(unique_counts)

# 🔢 إحصاءات عددية
print("\n🔢 الإحصاءات العددية:")
display(df.describe(include=[np.number]))

# 🎯 الأعمدة النوعية وتوزيعها (Top 5 فقط)
categorical_cols = df.select_dtypes(include='object').columns
for col in categorical_cols[:5]:
    print(f"\n🎯 العمود النوعي: {col}")
    print(df[col].value_counts().head(10))

    # رسم التوزيع
    plt.figure(figsize=(8, 4))
    sns.countplot(data=df, x=col, order=df[col].value_counts().index[:10])
    plt.title(f"Top 10 Values in '{col}'", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 📊 توزيع الأعمدة الرقمية (أول 5 فقط)
numeric_cols = df.select_dtypes(include=np.number).columns[:5]
df[numeric_cols].hist(figsize=(14, 10), bins=30, edgecolor='black')
plt.tight_layout()
plt.suptitle("📊 توزيعات أول 5 أعمدة رقمية", fontsize=16, y=1.02)
plt.show()

# 📘 تحديث سجل المصادر (اختياري من النوتبوك)
print("\n📘 تحديث سجل مصادر البيانات الخام (اختياري):")
try:
    register_module = importlib.import_module("data_intelligence_system.data.raw.register_sources")
    register_module.main()
    print("✅ تم تحديث سجل المصادر بنجاح.")
except Exception as e:
    print(f"❌ خطأ أثناء تحديث سجل المصادر: {e}")
# 00_data_overview.py

# 📌 إعدادات أساسية
from IPython import get_ipython
try:
    get_ipython().run_line_magic("pip", "install ipython")
except:
    pass  # يعمل فقط داخل Jupyter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from IPython.display import display
import importlib
import sys

# ⚙️ إعدادات العرض
pd.set_option('display.max_columns', 100)
sns.set(style="whitegrid")

# 📂 تحديد جذر المشروع وضبط sys.path
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]  # ✅ تصحيح المستوى
except NameError:
    PROJECT_ROOT = Path.cwd().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 📂 تحميل البيانات المنظفة
DATA_PATH = PROJECT_ROOT / "data_intelligence_system" / "data" / "processed" / "clean_data.csv"
print(f"مسار الملف المستخدم: {DATA_PATH}")
if not DATA_PATH.exists():
    raise FileNotFoundError(f"الملف غير موجود في المسار: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# ✅ عرض الشكل والمحتوى العام
print("✅ شكل البيانات:", df.shape)
display(df.head())

# 🔍 معلومات الأعمدة
print("\n🔍 معلومات الأعمدة:")
df.info()

# 📉 تحليل القيم المفقودة
print("\n📉 جدول القيم المفقودة:")
missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    "Missing Count": missing,
    "Missing %": missing_percent
})
missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values(by="Missing %", ascending=False)
display(missing_df)

# 📦 توزيع القيم الفريدة (Top 20)
print("\n📦 توزيع القيم الفريدة (Top 20):")
unique_counts = df.nunique().sort_values(ascending=False).head(20)
display(unique_counts)

# 🔢 إحصاءات عددية
print("\n🔢 الإحصاءات العددية:")
display(df.describe(include=[np.number]))

# 🎯 الأعمدة النوعية وتوزيعها (Top 5 فقط)
categorical_cols = df.select_dtypes(include='object').columns
for col in categorical_cols[:5]:
    print(f"\n🎯 العمود النوعي: {col}")
    print(df[col].value_counts().head(10))

    # رسم التوزيع
    plt.figure(figsize=(8, 4))
    sns.countplot(data=df, x=col, order=df[col].value_counts().index[:10])
    plt.title(f"Top 10 Values in '{col}'", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 📊 توزيع الأعمدة الرقمية (أول 5 فقط)
numeric_cols = df.select_dtypes(include=np.number).columns[:5]
df[numeric_cols].hist(figsize=(14, 10), bins=30, edgecolor='black')
plt.tight_layout()
plt.suptitle("📊 توزيعات أول 5 أعمدة رقمية", fontsize=16, y=1.02)
plt.show()

# 📘 تحديث سجل المصادر (اختياري من النوتبوك)
print("\n📘 تحديث سجل مصادر البيانات الخام (اختياري):")
try:
    register_module = importlib.import_module("data_intelligence_system.data.raw.register_sources")
    register_module.main()
    print("✅ تم تحديث سجل المصادر بنجاح.")
except Exception as e:
    print(f"❌ خطأ أثناء تحديث سجل المصادر: {e}")
# 00_data_overview.py

# 📌 إعدادات أساسية
from IPython import get_ipython
try:
    get_ipython().run_line_magic("pip", "install ipython")
except:
    pass  # يعمل فقط داخل Jupyter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from IPython.display import display
import importlib
import sys

# ⚙️ إعدادات العرض
pd.set_option('display.max_columns', 100)
sns.set(style="whitegrid")

# 📂 تحديد جذر المشروع وضبط sys.path
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]  # ✅ تصحيح المستوى
except NameError:
    PROJECT_ROOT = Path.cwd().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 📂 تحميل البيانات المنظفة
DATA_PATH = PROJECT_ROOT / "data_intelligence_system" / "data" / "processed" / "clean_data.csv"
print(f"مسار الملف المستخدم: {DATA_PATH}")
if not DATA_PATH.exists():
    raise FileNotFoundError(f"الملف غير موجود في المسار: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# ✅ عرض الشكل والمحتوى العام
print("✅ شكل البيانات:", df.shape)
display(df.head())

# 🔍 معلومات الأعمدة
print("\n🔍 معلومات الأعمدة:")
df.info()

# 📉 تحليل القيم المفقودة
print("\n📉 جدول القيم المفقودة:")
missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    "Missing Count": missing,
    "Missing %": missing_percent
})
missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values(by="Missing %", ascending=False)
display(missing_df)

# 📦 توزيع القيم الفريدة (Top 20)
print("\n📦 توزيع القيم الفريدة (Top 20):")
unique_counts = df.nunique().sort_values(ascending=False).head(20)
display(unique_counts)

# 🔢 إحصاءات عددية
print("\n🔢 الإحصاءات العددية:")
display(df.describe(include=[np.number]))

# 🎯 الأعمدة النوعية وتوزيعها (Top 5 فقط)
categorical_cols = df.select_dtypes(include='object').columns
for col in categorical_cols[:5]:
    print(f"\n🎯 العمود النوعي: {col}")
    print(df[col].value_counts().head(10))

    # رسم التوزيع
    plt.figure(figsize=(8, 4))
    sns.countplot(data=df, x=col, order=df[col].value_counts().index[:10])
    plt.title(f"Top 10 Values in '{col}'", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 📊 توزيع الأعمدة الرقمية (أول 5 فقط)
numeric_cols = df.select_dtypes(include=np.number).columns[:5]
df[numeric_cols].hist(figsize=(14, 10), bins=30, edgecolor='black')
plt.tight_layout()
plt.suptitle("📊 توزيعات أول 5 أعمدة رقمية", fontsize=16, y=1.02)
plt.show()

# 📘 تحديث سجل المصادر (اختياري من النوتبوك)
print("\n📘 تحديث سجل مصادر البيانات الخام (اختياري):")
try:
    register_module = importlib.import_module("data_intelligence_system.data.raw.register_sources")
    register_module.main()
    print("✅ تم تحديث سجل المصادر بنجاح.")
except Exception as e:
    print(f"❌ خطأ أثناء تحديث سجل المصادر: {e}")
