# licencpp

## Description

This tool is made for C++ projects with dependencies managed by vcpkg. It is designed to help you to audit your project's licenses and verify the solution compliance, thanks to ORT (OSS Review Tooklit) compatibility.

From the folder in which you have your vcpkg.json file, you can run the following command to generate a report of your project's licenses:

```bash
python /path/to/licencpp
/path/to/ort analyze -i . -o . -f JSON
```

If you need to install ORT, please refer to the [official documentation](https://oss-review-toolkit.org/ort/docs/getting-started/installation).

licencpp requires Python 3.6 or later and the following Python packages:

- pyyaml

