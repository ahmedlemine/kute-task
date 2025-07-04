import flet as ft
from api import TaskAPI
from db import sqlite_url
from models import Task

api = TaskAPI(sqlite_url)


class TaskControl(ft.Column):
    """custom control to represnt a single task item in the task list view"""

    def __init__(self, task, task_status_change, task_title_update, task_delete):
        super().__init__()
        self.task = task
        self.task_status_change = task_status_change
        self.task_title_update = task_title_update
        self.task_delete = task_delete

        self.display_task = ft.Checkbox(
            value=self.task.is_completed,
            label=self.task.title,
            on_change=self.status_changed,
        )
        # input box for edting task's name
        self.edit_name = ft.TextField(expand=1)

        # display of each task. A task is either in display or edit view
        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CREATE_OUTLINED,
                            tooltip="Edit Task",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip="Delete Task",
                            on_click=lambda e: self.delete_clicked(task.id),
                        ),
                    ],
                ),
            ],
        )

        # edit view of echa task. A task is either in display or edit view
        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.BLUE,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        self.controls = [self.display_view, self.edit_view]

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.task_title_update(self.task, self.display_task.label)
        self.display_view.visible = True
        self.edit_view.visible = False

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_status_change(self.task)

    def delete_clicked(self, e):
        self.task_delete(self, e)


class ListTasksView(ft.Column):
    """a view to display a list of task (each task represented by a TaskControl)
    with a tab for filtering and a textbox for adding new tasks"""

    def __init__(self, get_task_list_from_db):
        super().__init__()
        self.new_task = ft.TextField(
            hint_text="What needs to be done?",
            on_submit=self.add_clicked,
            expand=True,
            max_length=30,
        )
        self.tasks = ft.ListView(spacing=0, auto_scroll=False, expand=True)

        self.get_task_list_from_db = get_task_list_from_db

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="all"), ft.Tab(text="active"), ft.Tab(text="completed")],
        )

        self.items_left = ft.Text("0 items left")

        self.width = 360
        self.height = 760
        self.controls = [
            ft.Row(
                [
                    ft.ElevatedButton("Back", on_click=lambda _: self.page.go("/")),
                ]
            ),
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        icon=ft.Icons.ADD, on_click=self.add_clicked
                    ),
                ],
            ),
            ft.Container(
                expand=True,
                content=ft.Column(
                    spacing=25,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        self.filter,
                        self.tasks,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.items_left,
                                ft.OutlinedButton(
                                    text="Clear completed",
                                    on_click=self.clear_clicked,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        ]

    def add_clicked(self, e):
        if self.new_task.value:
            task = Task(title=self.new_task.value)
            added_task_id = api.add_task(task)
            added_task = api.get_task(str(added_task_id))
            self.page.open(ft.SnackBar(ft.Text("New task added.")))

            task_control = TaskControl(
                added_task,
                self.task_status_change,
                self.task_title_update,
                self.task_delete,
            )
            self.tasks.controls.append(task_control)
            self.new_task.value = ""
            self.new_task.focus()
            self.update()

    def task_status_change(self, task):
        updated_task = api.toggle_complete(str(task.id))
        task.is_completed = updated_task.is_completed
        self.update()

    def task_title_update(self, task, title):
        updated_task = api.update_task_title(str(task.id), title)
        self.page.open(ft.SnackBar(ft.Text("Task updated.")))
        task.title = updated_task.title
        self.update()

    def task_delete(self, task_item, task_id):
        api.delete_task(str(task_id))
        self.page.open(ft.SnackBar(ft.Text("Task deleted.")))
        self.tasks.controls.remove(task_item)
        self.update()

    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        for t in self.tasks.controls[:]:
            if t.task.is_completed:
                self.task_delete(t, t.task.id)

    def build(self):
        self.tasks.controls.clear()
        if not len(self.tasks.controls):
            for task in self.get_task_list_from_db():
                task_item = TaskControl(
                    task,
                    self.task_status_change,
                    self.task_title_update,
                    self.task_delete,
                )
                self.tasks.controls.append(task_item)

    def before_update(self):
        self.task_list_from_db = self.get_task_list_from_db()
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for t in self.tasks.controls:
            t.visible = (
                status == "all"
                or (status == "active" and t.task.is_completed == False)
                or (status == "completed" and t.task.is_completed)
            )
            if not t.task.is_completed:
                count += 1
        self.items_left.value = f"{count} task(s) left of {api.count_tasks()} total"
