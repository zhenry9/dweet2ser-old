from setup_config import DweetConfiguration


def main():
    cfg = DweetConfiguration().parser
    cfg.setup()


if __name__ == '__main__':
    main()
