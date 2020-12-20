import optparse


def new_parser() -> optparse.OptionParser:
    parser = optparse.OptionParser(usage="%prog -d <days of age to purge>")
    parser.set_defaults(
        days=0,
        trash_path=None,
        max_free=0,
        delete=0,
        min_free=0,
        verbose=False,
        quiet=False,
        check=False,
        dryrun=False,
        stat=False,
        delete_first=[],
        version=False,
        trash_limit=0,
    )
    parser.add_option(
        "-d",
        "--days",
        dest="days",
        type="int",
        help="delete files older then DAYS number of days.",
        metavar="DAYS",
    )
    parser.add_option(
        "-T",
        "--trash-path",
        dest="trash_path",
        help="empty the trash path in the given DIRECTORY instead of using the user home directory",
        metavar="DIRECTORY",
    )
    parser.add_option(
        "-t",
        "--trash-mounts",
        dest="trash_mounts",
        action="store_true",
        default=False,
        help="Process all user trash directories instead of just the one in the home directory",
    )
    parser.add_option(
        "--max-free",
        dest="max_free",
        type="int",
        help="only run if less then M megabytes of free space is left.",
        metavar="M",
    )
    parser.add_option(
        "--delete",
        dest="delete",
        type="int",
        help="delete at least M megabytes.",
        metavar="M",
    )
    parser.add_option(
        "--min-free",
        "--keep-free",
        dest="min_free",
        type="int",
        help="set --delete to make sure M megabytes of space is available.",
        metavar="M",
    )
    parser.add_option(
        "--trash_limit",
        dest="trash_limit",
        type="int",
        help="make sure no more than M megabytes of space are used by the trash.",
        metavar="M",
    )
    parser.add_option(
        "-D",
        "--delete-first",
        action="append",
        dest="delete_first",
        help="push files matching this REGEX to the top of the deletion queue",
        metavar="REGEX",
    )
    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="be more verbose, a must when testing something out",
    )
    parser.add_option(
        "-q", "--quiet", action="store_true", dest="quiet", help="only output warnings"
    )
    parser.add_option(
        "--check",
        action="store_true",
        dest="check",
        help="report .trashinfo files without a real file",
    )
    parser.add_option(
        "--dry-run",
        action="store_true",
        dest="dryrun",
        help="just list what would have been done",
    )
    parser.add_option(
        "--stat",
        action="store_true",
        dest="stat",
        help="show the number, and total size of files involved",
    )
    parser.add_option(
        "-V",
        "--version",
        action="store_true",
        dest="version",
        help="show version and exit",
    )
    parser.add_option(
        "--install",
        action="store_true",
        dest="install",
        help="set autotrash to run automatically with the given options",
    )
    return parser


def check_options(parser, options) -> None:
    if options.delete + options.min_free + options.days == 0:
        parser.error(
            "You need to specify at least one of:\n"
            "\t -d <days of age to purge>,\n"
            "\t --delete <number of megabytes to purge>, or\n"
            "\t --min-free <number of megabytes to make free>\n"
            "for this command to have any effect."
        )

    if options.days < 0:
        parser.error("Can not work with a negative or zero days")

    if options.max_free < 0:
        parser.error("Can not work with a negative value for --max-free")

    if options.delete < 0:
        parser.error("Can not work with a negative value for --delete")

    if options.min_free < 0:
        parser.error("Can not work with a negative value for --min-free")

    if options.trash_limit < 0:
        parser.error("Can not work with a negative value for --trash_limit")

    if options.trash_path and options.trash_mounts:
        parser.error("Cannot auto-detect trash directories when setting a specific one")

    if options.stat and options.quiet:
        parser.error("Specifying both --quiet and --stat does not make sense")

    if options.verbose and options.quiet:
        parser.error("Specifying both --quiet and --verbose does not make sense")

    if options.delete and options.min_free:
        parser.error(
            "Combining --delete and --min-free results in unpredictable behaviour\n"
            " as --delete may or may not be ignored depending on the free space."
        )

    if options.trash_limit and (options.delete or options.min_free):
        parser.error(
            "Combining --trash_limit with --min-free or --delete is unsupported\n"
            "as these rules may contradict each other."
        )

    if (not options.min_free) and options.delete_first:
        parser.error(
            "Using --delete-first (-D) without --min-free does not have any effect.\n"
            "Age based purging will still work as predicted."
        )
