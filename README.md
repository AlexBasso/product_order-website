# Online product/order website with various API

This website has many functionalities and very little in terms of frontend. This website can act as product and orders
display/database for CRUD operations, as a blog, supports user accounts and file upload/download, it also has several
minor API endpoints for testing purposes.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install poetry, then use poetry to install all
dependencies.

```bash
pip install poetry
poetry install
```

Before use, you need:

1. Fill in  ".env.template" and rename it to ".env"

You are all set to go!

## This is how it looks

![Test image](shop_api.jpg)

## Usage

Site is ready for deployment on a hosting server with docker using gunicorn, for more information refer to Dockerfile
and docker-compose.yaml.

## Contributing

Pull requests are welcome. This was my first website/store project, it was fun.

## License

[MIT](LICENSE.txt)