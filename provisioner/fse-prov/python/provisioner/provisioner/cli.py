"""
Helper function to create click commands
"""

import logging

import click

from provisioner import log_utils

_CLICK_CONTEXT_SETTINGS = {"help_option_names": ["--help", "-h"]}


def command(default_log_level=logging.DEBUG):
    """
    Create a provisioner CLI command. This is a decorator, to be used in place
        of @click.command. When called, it provides a help option include short
        form, i.e. `-h | --help`, as well as some options common to all commands.
        See each option's documentation for details.

    Example usage:
        ```
        @cli.command(default_log_level)
        @click.option("--extra")
        def my_command(LOG, verbose, extra):
            LOG.info("It's working!")
            if verbose:
                LOG.info(f"Extra option: {extra}")
        ```

    Args:
        default_log_level (int): The default log level for the CLI command
            [default: logging.DEBUG]
    """
    return _combine_decorators(
        click.command(context_settings=_CLICK_CONTEXT_SETTINGS),
        verbosity_option(),
        logging_option(default=default_log_level),
    )


def _combine_decorators(*inner_decorators):
    def outer_decorotor(wrapped_function):
        for decorator in reversed(inner_decorators):
            wrapped_function = decorator(wrapped_function)
        return wrapped_function

    return outer_decorotor


def logging_option(default=logging.DEBUG):
    """
    Add a hidden `-l | --log-level` click option to a command. A logger named
    after the command will be initialized using the provided log level, and
    passed into the function as the parameter `LOG`.

    Example usage:
        ```
        @click.command()
        @cli.logging_option(default=logging.WARNING)
        def my_command(LOG):
            LOG.info("It's working!")
        ```

    Args:
        default (int): The default log level to use if none is set on the command
            line [default: logging.INFO]
    """

    def convert_and_init_log_level(ctx, param, value):
        level_value = logging.getLevelName(value.upper())
        if not isinstance(level_value, int):
            raise click.BadOptionUsage(
                param.option_name, f"Invalid {param.option_name} specified", ctx=ctx
            )

        verbose = ctx.obj and ctx.obj.get("verbose")
        console_level = logging.DEBUG if verbose else logging.INFO

        log_utils.initialize(ctx.info_name, level_value, console_level=console_level)
        return logging.getLogger(ctx.info_name)

    return click.option(
        "--log-level",
        "-l",
        "LOG",
        hidden=True,
        help="Set the log level for this command",
        default=logging.getLevelName(default),
        type=click.Choice(
            [
                logging.getLevelName(lvl)
                for lvl in [
                    logging.CRITICAL,
                    logging.ERROR,
                    logging.WARNING,
                    logging.INFO,
                    logging.DEBUG,
                ]
            ],
            case_sensitive=False,
        ),
        callback=convert_and_init_log_level,
    )


def verbosity_option():
    """
    Add a `-v | --verbose` click flag to a command.

    NOTE: To set the console log level, this must be used BEFORE `logging_option`
    when decorating a click command.

    Example usage:
        ```
        @click.command()
        @cli.verbosity_option()
        def my_command(verbose):
            if verbose:
                print("Lots of details")
            else:
                print("The basics")
        ```
    """

    # Pass the value through context so that the log setup can use it
    def set_verbose_ctx(ctx, _param, value):
        if ctx.obj is None:
            ctx.obj = {}
        ctx.obj["verbose"] = value

    return click.option(
        "--verbose",
        "-v",
        help="Print more details while running, and more detailed summary of results.",
        is_flag=True,
        callback=set_verbose_ctx,
    )


def validate_stores(ctx, _param, value):
    """
    Validate that at least one store was specified on the command line.

    Example usage:
        ```
        @click.command()
        @click.argument("stores", callback=cli.validate_stores, nargs=-1)
        def my_command(stores):
            for store in stores:
                print(store)
        ```
    """
    if len(value) == 0:
        raise click.BadArgumentUsage("Must specify at least one store", ctx=ctx)

    return list(value)
