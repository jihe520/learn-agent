# Pytest 使用教程（从入门到实战）

## 一、什么是 pytest？

**pytest** 是 Python 生态中最流行的测试框架之一，特点是：

* ✅ 语法简洁（用 `assert` 即可）
* ✅ 自动发现测试用例
* ✅ 强大的 fixture（依赖注入）
* ✅ 原生支持参数化、mock、插件
* ✅ 非常适合现代 Python 项目（包括 agent / AI 项目）

一句话总结：

> **pytest 让“写测试”这件事变得不痛苦。**

---

## 二、安装与第一个测试

### 1. 安装 pytest

```bash
uv add pytest
```

### 2. 编写第一个测试

#### math_utils.py

```python
def add(a, b):
    return a + b
```

#### test_math_utils.py

```python
from math_utils import add

def test_add():
    assert add(1, 2) == 3
```

运行测试：

```bash
uv run pytest
```

pytest 会自动：

* 查找 `test_*.py` 或 `*_test.py`
* 查找以 `test_` 开头的函数
* 执行并汇总结果

---

## 三、pytest 的基本规则

### 1. 测试文件命名

* `test_xxx.py`
* `xxx_test.py`

### 2. 测试函数命名

```python
def test_something():
    ...
```

### 3. 使用原生 assert

```python
assert result == expected
```

pytest 会在失败时自动给出**详细对比信息**。

---

## 四、fixture：pytest 的核心能力

fixture 用于**准备测试环境、共享依赖、管理资源生命周期**。

### 1. 定义 fixture

```python
import pytest

@pytest.fixture
def sample_list():
    return [1, 2, 3]
```

### 2. 使用 fixture（像函数参数一样）

```python
def test_list_length(sample_list):
    assert len(sample_list) == 3
```

👉 pytest 会自动把 fixture 注入测试函数。

---

### 3. fixture 的作用域（scope）

```python
@pytest.fixture(scope="function")  # 默认
@pytest.fixture(scope="module")
@pytest.fixture(scope="session")
```

常见用途：

* function：普通单元测试
* module：昂贵初始化（如大模型）
* session：数据库、全局资源

---

## 五、参数化测试（强烈推荐）

当你想用**多组数据测试同一逻辑**时：

```python
import pytest

@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
    ]
)
def test_add_param(a, b, expected):
    assert a + b == expected
```

优点：

* 避免重复代码
* 覆盖更多边界情况
* 测试报告更清晰

---

## 六、异常测试

### 1. 断言抛出异常

```python
import pytest

def div(a, b):
    return a / b

def test_div_zero():
    with pytest.raises(ZeroDivisionError):
        div(1, 0)
```

### 2. 检查异常信息

```python
with pytest.raises(ValueError, match="invalid"):
    raise ValueError("invalid input")
```

---

## 七、mock：隔离外部依赖（非常重要）

### 1. 为什么要 mock？

测试中**不应该**：

* 调真实 API
* 访问数据库
* 请求网络
* 调用 LLM

### 2. 使用 unittest.mock

```python
from unittest.mock import Mock

def test_with_mock():
    api = Mock()
    api.call.return_value = "ok"

    result = api.call("hello")
    assert result == "ok"
    api.call.assert_called_once_with("hello")
```

---

### 3. 使用 pytest monkeypatch

```python
def test_monkeypatch(monkeypatch):
    def fake_time():
        return 123

    monkeypatch.setattr("time.time", fake_time)

    import time
    assert time.time() == 123
```

⚠️ 记住原则：

> **patch 使用点，而不是定义点**

---

## 八、conftest.py：全局 fixture 管理

在 `tests/conftest.py` 中定义的 fixture：

* 不需要 import
* 所有测试自动可用

```python
# tests/conftest.py
import pytest

@pytest.fixture
def config():
    return {"env": "test"}
```

```python
def test_config(config):
    assert config["env"] == "test"
```

---

## 九、测试标记（mark）

### 1. 自定义标记

```python
@pytest.mark.slow
def test_slow():
    ...
```

运行时过滤：

```bash
pytest -m "not slow"
```

### 2. 跳过测试

```python
@pytest.mark.skip(reason="not ready")
def test_skip():
    ...
```

### 3. 条件跳过

```python
@pytest.mark.skipif(sys.platform == "win32", reason="windows issue")
```

---

## 十、pytest 常用命令行参数

```bash
pytest                 # 运行全部
pytest tests/test_a.py # 指定文件
pytest -k add          # 模糊匹配测试名
pytest -x              # 首次失败即停止
pytest -s              # 显示 print 输出
pytest -vv             # 更详细输出
```

---

## 十一、pytest 在真实项目中的推荐结构

```text
project/
├── src/
│   └── app/
│       └── core.py
├── tests/
│   ├── test_core.py
│   └── conftest.py
├── pyproject.toml
```

在 `pyproject.toml` 中配置 pytest：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## 十二、pytest 最佳实践总结

### 推荐

* ✅ 小而快的单元测试
* ✅ 使用 fixture 管理依赖
* ✅ mock 外部系统
* ✅ 参数化覆盖边界

### 不推荐

* ❌ assert 大段字符串（尤其是 LLM 输出）
* ❌ 单测里调真实 API
* ❌ 一个测试验证多个行为

---

## 十三、什么时候 pytest 特别适合？

* Web 后端（FastAPI / Django）
* 数据处理
* Agent / AI 项目
* SDK / 工具库
* CI / 自动化测试
