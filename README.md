# statcert
Fetch information about domains and their TLS certificates.

## Installation
To install statcert, ensure you have Python v3.8 or greater and pip installed in your system. Then, simply run
```
pip install statcert
```

## Basic Usage
Statcert fetches information from a list of domains.
This list of domains can either be provided by the user as command line arguments
(e.g.: `statcert google.com twitter.com github.com`);
provided by the user as a file (e.g.: `statcert path/to/domain-list.txt`);
or fetched from the latest [Tranco list](https://tranco-list.eu) top 1 million websites,
by not specifying any list at all (i.e. running just `statcert`, without any arguments).

The operation can be cancelled halfway by pressing Ctrl+C while the program is executing. The program will
halt immediatly any ongoing operations;
save the partial results to a file, if required;
print a summary of the partial results;
and then terminate.

It's also possible to determine how many domains should be fetched from the provided list using the `-n` option.
This can be done by just specyfing the number of domain (e.g.: `statcert -n 100` will fetch information on the top 100 domains from the Tranco list), or by specifying an inclusive range of certificates (e.g.: `statcert long-domain-list.txt -n 100-199` will fetch information from the 100th domain to the 199th in `long-domain-list.txt`).

To save the fetched information, you can specify a file with the `-o` option. The output format will be inferred from the termination of the file, and the supported formats are `.txt`, `.csv` and `.json`.

By default, statcert will change how much information is displayed depending on the arguments used, but this can be personalized with the `-q` and `-v` options, which will display nothing at all or as much information as available respectivelly.

In order to check all the available output options and their descriptions, run
```
statcert -h
```

## Development
To set up the development environment, first make sure you have Python version 3.8 or higher installed and both `python` and `pip` are on your PATH.

Then, create and activate a virtual environment for development. This can be done by running

    python -m venv venv

and then either `source venv/bin/activate`, in Linux and MacOS, or `venv\Scripts\activate.bat`, in Windows.

Finally, install the development dependencies using the requirements files. This can be done by running

    pip install -r requirements.txt
