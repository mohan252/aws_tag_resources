import sys
import os


from consolemenu import *
from consolemenu.format import *
from consolemenu.items import *

from common import continue_prompt
import aws_region
import aws_profile
import dynamo_table
import tags


def set_region():
    print(f"Current Region is {aws_region.get()}")
    new_region = input("Enter New Region : ")
    aws_region.set(new_region)
    print(f"Region set to {aws_region.get()}")
    continue_prompt()


def print_region():
    print(f"Current Region is {aws_region.get()}")
    continue_prompt()


def set_profile():
    print(f"Current Profile is {aws_profile.get()}")
    new_profile = input("Enter New profile : ")
    aws_profile.set(new_profile)
    print(f"Profile set to {aws_profile.get()}")
    continue_prompt()


def print_profile():
    print(f"current profile is {aws_profile.get()}")
    continue_prompt()


def main():
    menu_format = (
        MenuFormatBuilder()
        .set_border_style_type(MenuBorderStyleType.HEAVY_BORDER)
        .set_prompt("SELECT>")
        .set_title_align("center")
        .set_subtitle_align("center")
        .set_left_margin(4)
        .set_right_margin(4)
        .show_header_bottom_border(True)
    )

    menu = ConsoleMenu(
        "AWS Tagging",
        "Utlity to help tag AWS resource",
        formatter=menu_format,
    )

    function_item_1 = FunctionItem("Set the target AWS Region", set_region)

    function_item_2 = FunctionItem(
        "Display the target AWS Region",
        print_region,
    )

    function_item_3 = FunctionItem("Set the AWS Profile", set_profile)

    function_item_4 = FunctionItem(
        "Display the current AWS Profile",
        print_profile,
    )

    function_item_5 = FunctionItem(
        "Create the DynamoDB Table",
        lambda: dynamo_table.create(),
    )

    function_item_6 = FunctionItem(
        "Delete DynamoDB Table",
        lambda: dynamo_table.delete(),
    )

    function_item_7 = FunctionItem(
        "Delete all records from DynamoDB Table",
        lambda: dynamo_table.delete_all_records(),
    )

    function_item_8 = FunctionItem(
        "Load the AWS Resource tags into the table Aws_RscTag_Tbl",
        lambda: tags.load_resources(),
    )

    function_item_9 = FunctionItem(
        "Export the data  Aws_RscTag_Tbl to a CSV file Aws_ResourceTag.csv",
        lambda: dynamo_table.export_csv("Aws_ResourceTag.csv"),
    )

    function_item_10 = FunctionItem(
        "Import and Replace the data from a csv file [Aws_ResourceTag.csv]",
        lambda: dynamo_table.import_data_from_csv("Aws_ResourceTag.csv", replace=True),
    )

    function_item_11 = FunctionItem(
        "Import and Append  the data from a csv file [Aws_ResourceTag.csv]",
        lambda: dynamo_table.import_data_from_csv("Aws_ResourceTag.csv", replace=False),
    )

    function_item_12 = FunctionItem(
        "Apply the AWS DynamoDB Table to the AWS Resources",
        lambda: tags.apply(),
    )

    menu.append_item(function_item_1)
    menu.append_item(function_item_2)
    menu.append_item(function_item_3)
    menu.append_item(function_item_4)
    menu.append_item(function_item_5)
    menu.append_item(function_item_6)
    menu.append_item(function_item_7)
    menu.append_item(function_item_8)
    menu.append_item(function_item_9)
    menu.append_item(function_item_10)
    menu.append_item(function_item_11)
    menu.append_item(function_item_12)
    menu.show()


if __name__ == "__main__":
    main()