import argparse
import logging
from docstrings import DocstringService


def get_arguments():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Create, update, or validate docstrings in Python files.")

    parser.add_argument('-a', '--attempts', type=int, default=5, metavar='[1-100]',
                        help='Set the number of attempts for processing. Must be an integer in the range [1..100].')
    parser.add_argument('-c', '--create', action='store_true',
                        help='Create new docstrings for functions that do not currently have one.')
    parser.add_argument('-d', '--depth', type=int, default=1, metavar='[1-100]',
                        help='Set the depth for processing. Must be an integer in the range [1..100].')
    parser.add_argument('-l', '--log-level', type=int, default=0, choices=range(0, 3),
                        help='Set the log level. 0 = no logs, 1 = brief logs, 2 = verbose logs')
    parser.add_argument('-m', '--modify', action='store_true',
                        help='Modify the original files with new changes. If -p is also specified, will prompt user before modifying the file.')
    parser.add_argument('-p', '--preview', action='store_true',
                        help='Preview the content of the files without making changes unless -m is also specified, in which case it will prompt user before modifying the file.')
    parser.add_argument('-r', '--report', action='store_true',
                        help='Show report after each file is processed.')
    parser.add_argument('-u', '--update', action='store_true',
                        help='Update existing docstrings. If -v is specified, will only update if current docstring failed validation.')
    parser.add_argument('-v', '--validate', action='store_true',
                        help='Validate that the docstrings in the file correctly describe the source code. If -u is also specified, update will only occur if validation fails.')
    
    # Adding positional argument for filenames
    parser.add_argument('filenames', nargs='*',
                        help='List of filenames to process. If an undecorated filename is provided, all functions in the file will be examined. The limit the scope of operations, filenames can be decorated by add a colon-separated list of function paths of the form foo.bar.zoo, where foo, bar, and zoo can be the names of functions or classes. Nesting of functions and classes is allowed. If a path is longer than the --depth field,a warning is reported and the function is not processed.')

    # Parse the arguments
    args = parser.parse_args()

    with open('samples/example_docstring.txt', 'r') as infile:
        args.example_docstring = infile.read()
    with open('samples/example_function.txt', 'r') as infile:
        args.example_function = infile.read()

    return args


def get_logger(args):
    logger = logging.getLogger(__name__)
    if args.log_level == 0:
        logger.setLevel(logging.CRITICAL)  # No logs shown
    elif args.log_level == 1:
        logger.setLevel(logging.INFO)  # Brief logs
    elif args.log_level == 2:
        logger.setLevel(logging.DEBUG)  # Verbose logs

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def main():
    """
    This script processes the docstrings of Python functions using a set of command line options. The main function parses these options, sets up a logger, creates an instance of the DocstringService class, and then iterates over each file to be processed.
    
    The process_file function is responsible for processing each file's docstrings based on the options provided. It can create new docstrings, update existing ones, or validate that the existing docstrings are correct. The results of these operations are reported if the report option is enabled.
    
    Finally, after all files have been processed, a report of any errors encountered during processing will be printed out. If the modify option is enabled and no preview option was specified, then the script will prompt the user for confirmation before making any changes to the files.
    """
    
    args = get_arguments()
    logger = get_logger(args)
        
    # Create the docstring service
    docstring_service = DocstringService(args, logger)

    # Process each file with the document_file function
    for decorated_filename in args.filenames:
        parts = decorated_filename.split(':')
        filename = parts[0]
        function_paths = None if len(parts) <= 1 else parts[1:]
        # Call the document_file function with the filename and list of options
        modified_file, reports = docstring_service.document_file(filename, function_paths)
        if args.preview:
            print(modified_file)

        if args.modify:
            save_file = not args.preview
    
            # Only ask for user confirmation if 'preview' option is enabled
            if args.preview:
                user_response = input(f'\nDo you want to save these modifications to {filename}? (y/N) ').strip().lower()
                # Set the save_file flag based on user input
                save_file = (user_response == 'y')

            # Check the save_file flag to decide whether to save the file
            if save_file:
                with open(filename, 'w') as outfile:
                    outfile.write(modified_file)
                print(f'Updated {filename}')
            else:
                print(f'{filename} was NOT updated.')
        
        if args.report and reports is not None and len(reports) > 0:
            print('-' * 79)
            for report in reports:
                print(report)


if __name__ == '__main__':
    main()
