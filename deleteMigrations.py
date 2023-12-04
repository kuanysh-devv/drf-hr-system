import os
import shutil


def delete_migrations(package_name, app_names):
    for app_name in app_names:
        migrations_path = os.path.join(package_name, app_name, 'migrations')

        # Ensure the migrations folder exists
        if os.path.exists(migrations_path):
            # Get all files in the migrations folder except __init__.py
            files_to_delete = [f for f in os.listdir(migrations_path) if f != '__init__.py']

            # Delete each file in the migrations folder
            for file_name in files_to_delete:
                file_path = os.path.join(migrations_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            print(f"Migrations deleted for {app_name}")
        else:
            print(f"No migrations found for {app_name}")


if __name__ == "__main__":
    package_name = 'C:/Users/User4/PycharmProjects/drf-hr-system'  # need to change
    app_names = ['birth_info', 'decree', 'docx_generator', 'education', 'filter', 'identity_card_info', 'location',
                 'military_rank', 'person', 'photo', 'position', 'resident_info', 'staffing_table', 'working_history']

    delete_migrations(package_name, app_names)
