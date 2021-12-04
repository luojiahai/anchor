# Anchor Programming Language

## Building and Installing

> Anchor requires Python 3.9 or later

### PyPI [Recommended]

Install the latest release from [The Python Package Index (PyPI)](https://pypi.org/project/anpl/):
```
pip install anpl
```

### Build and install locally

Run the following commands in order:
```
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m build
pip install ./dist/anchor-<version>.tar.gz --force-reinstall
```

---

## Running

Run the Anchor compiler:
```
an [option] [file]
```

> `an --help` for more information

---

## Getting Started

This is an example of the Anchor code to print `Hello, World!`:
```
print("Hello, World!");
```

This is an example of the Anchor code to define a class:
```
class[public] MyClass
begin
    property[public, get, set] x: Integer;

    method[public, factory] MyClass() -> MyClass
    begin
        this.x = 0;
        this.printSomething();
        return this;
    end

    method[public, factory] MyClass(x: Integer) -> MyClass
    begin
        this.x = x;
        return this;
    end

    method[private] printSomething() -> Null
    begin
        print("this is a private method");
    end
end
```

This is an example of the legacy function definition to return a string:
```
function myFunc() -> String
begin
    return "a legacy function";
end
```

---

## Contributing

I am excited to work alongside you to build and enhance Anchor Programming Language\!

***BEFORE you start work on a feature/fix***, please read and follow the [Contributor's Guide](./CONTRIBUTING.md) to help avoid any wasted or duplicate effort.

---

## Code of Conduct

This project has adopted the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md). For more information contact [luo@jiahai.co](mailto:luo@jiahai.co) with any additional questions or comments.
