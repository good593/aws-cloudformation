from setuptools import setup

setup(
    name="common",
    version="1.1.0",
    description="common library",
    url="https://git-codecommit.ap-northeast-2.amazonaws.com/v1/repos/pip-install-base",
    author="good593",
    author_email="good593@gmail.com",
    license="smart dev 4 team",
    packages=["common"],
    zip_safe=False,
    install_requires=[
        "boto3==1.17.50",
        "botocore==1.20.50",
        "aws-psycopg2==1.2.1",
        "requests==2.25.1",
        "black==20.8b1",
        "pytz==2021.1"
    ],
)
