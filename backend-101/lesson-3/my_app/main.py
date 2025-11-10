from utils.helpers import (
    brush_teeth,
    do_laundry,
    make_coffee,
    cook_omelet,
    prepare_backpack,
    start_day,
    pretty_print_steps,
)

def main() -> None:
    pretty_print_steps("Brushing Teeth", brush_teeth())
    pretty_print_steps("Doing Laundry", do_laundry())
    pretty_print_steps("Making Coffee", make_coffee())
    pretty_print_steps("Cooking Omelet", cook_omelet())
    pretty_print_steps("Preparing Backpack", prepare_backpack())

    # Bonus: nested calls
    pretty_print_steps("Start Day (nested functions)", start_day())

if __name__ == "__main__":
    main()