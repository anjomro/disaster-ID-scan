# Disaster ID Scan

[![PyPI - Version](https://img.shields.io/pypi/v/disaster-id-scan.svg)](https://pypi.org/project/disaster-id-scan)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/disaster-id-scan.svg)](https://pypi.org/project/disaster-id-scan)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install disaster-id-scan
```

## Usage

Currently the scanner only features the scanning mode. It can be started as follows, given that the package is [installed](#installation):


```console
disaster-id-scan scan
```

This will use the first camera available. To select a specific camera, use the `--cam` option:

```console
disaster-id-scan scan --cam 1
```

## License

`disaster-id-scan` is distributed under the terms of the [EUPL-1.2](https://spdx.org/licenses/EUPL-1.2.html) license.
