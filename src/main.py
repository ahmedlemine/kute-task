import flet as ft
from api import TaskAPI
from db import sqlite_url
from models import Task
from task_list_view import ListTasksView


class Drawer(ft.NavigationDrawer):
    def __init__(self, handle_drwr_change):
        super().__init__()
        self.on_change = handle_drwr_change
        self.controls = [
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="Choose Task",
                icon=ft.Icons.EXPLORE_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.EXPLORE),
            ),
            ft.NavigationDrawerDestination(
                label="Current Task",
                icon=ft.Icons.WATCH_LATER_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.WATCH_LATER),
            ),
            ft.NavigationDrawerDestination(
                label="Task List",
                icon=ft.Icon(ft.Icons.LIST),
                selected_icon=ft.Icons.LIST_OUTLINED,
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Settings",
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED),
                selected_icon=ft.Icons.SETTINGS,
            ),
            ft.NavigationDrawerDestination(
                label="About",
                icon=ft.Icon(ft.Icons.INFO_OUTLINE),
                selected_icon=ft.Icons.INFO,
            ),
        ]


# info for /about view
about = {
    "name": "Kute Task",
    "version": "0.1.0",
    "author": "Ahmed Lemine",
    "email": "ahmed.lemine@yahoo.com",
    "description": "A task tracking app that shows you only one task at a time and lets you choose to do it or defer it.",
    "supportme_url": "https://buymeacoffee.com/ahmedlemine",
}


class MainApp(ft.View):
    def __init__(self, api, page):
        super().__init__()
        self.api = api
        page.on_route_change = self.route_change
        self.drawer = Drawer(self.handle_drwr_change)
        self.task_list = self.get_task_list_from_db()
        self.routes = ["/", "/focus", "/list", "/settings", "/about"]
        self.single_task_item = self.get_single_task_item()
        self.current_focus_task = None

        # controls
        self.single_task_display_text = ft.Text(
            value=self.single_task_item.title
            if self.single_task_item is not None
            else "no remaining tasks",
            theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
            max_lines=3,
            width=320,
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(overflow=ft.TextOverflow.VISIBLE),
        )

        # / view
        self.empty_home_view_add_fab_btn = ft.Container(
            content=ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                on_click=self.add_new_task_fab_clicked,
            ),
            expand=True,
            alignment=ft.Alignment(1.0, 1.0),
            padding=ft.padding.all(10),
        )

        self.add_new_task_textfield = ft.TextField(
            label="Task Title",
            on_submit=lambda e: self.add_new_task(e),
            expand=True,
            max_length=30,
        )

        self.select_task_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            value="What task do you want to do now?",
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.Colors.GREY_500,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=ft.Row(
                        [self.single_task_display_text],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=20,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Do Now",
                            on_click=self.set_current_focus_task,
                            width=200,
                            style=ft.ButtonStyle(
                                padding=20,
                                bgcolor=ft.Colors.INDIGO,
                                color=ft.Colors.WHITE,
                                text_style=ft.TextStyle(size=24),
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Defer",
                            on_click=lambda e: self.defer_task(
                                self.get_single_task_item(), e
                            ),
                            width=200,
                            style=ft.ButtonStyle(
                                padding=20,
                                text_style=ft.TextStyle(size=24),
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [self.empty_home_view_add_fab_btn],
                    expand=True,
                ),
                ft.Row([ft.Container(height=50, expand=True)]),
            ],
            expand=True,
            alignment=ft.CrossAxisAlignment.CENTER,
            visible=self.get_single_task_item() is not None,
        )

        self.current_task_display = ft.Text(
            value=self.current_focus_task.title
            if self.current_focus_task is not None
            else "no task selected.",
            max_lines=5,
            width=320,
            text_align=ft.TextAlign.CENTER,
            theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
            style=ft.TextStyle(overflow=ft.TextOverflow.VISIBLE),
            visible=self.current_focus_task is not None,
        )

        self.empty_current_task_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            value="no task selected.",
                            text_align=ft.TextAlign.CENTER,
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            alignment=ft.CrossAxisAlignment.STRETCH,
            visible=self.current_focus_task is None,
        )

        self.current_task_done_btn = ft.ElevatedButton(
            "Done",
            on_click=self.finish_current_task,
            width=200,
            visible=False,
            style=ft.ButtonStyle(padding=20, text_style=ft.TextStyle(size=18)),
        )

        self.empty_tasks_home_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            border=ft.border.all(1, "indigo"),
                            border_radius=5,
                            padding=20,
                            content=ft.Text(
                                value="No unfinished tasks to select from.\n "
                                + "Please use the '+' button to go to the 'Task List'\n "
                                + "and add at least two tasks to start,\n"
                                + "\n"
                                + "Then use 'Choose Task' from the side menu\n"
                                + "to come back to this view and do your tasks\n"
                                + "one at a time",
                                theme_style=ft.TextThemeStyle.BODY_LARGE,
                                color=ft.Colors.GREY_600,
                                max_lines=7,
                                width=320,
                                text_align=ft.TextAlign.CENTER,
                                style=ft.TextStyle(overflow=ft.TextOverflow.VISIBLE),
                            ),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [self.empty_home_view_add_fab_btn],
                    expand=True,
                ),
                ft.Row([ft.Container(height=50, expand=True)]),
            ],
            expand=True,
            alignment=ft.CrossAxisAlignment.CENTER,
            visible=self.get_single_task_item() is None,
        )
        # /focus View
        self.focus_mode_title = ft.Text(
            value="currently wroking on:",
            visible=self.current_focus_task is not None,
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            style=ft.TextStyle(color=ft.Colors.GREY_600),
        )
        self.focus_mode_view = ft.Column(
            [
                ft.Row(
                    [self.focus_mode_title],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [self.current_task_display, self.empty_current_task_view],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [self.current_task_done_btn],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.CrossAxisAlignment.CENTER,
        )

        # /list: Task list view:
        self.task_list_control = ListTasksView(
            get_task_list_from_db=self.get_task_list_from_db
        )
        self.task_list_view = ft.Row([self.task_list_control])

        # /settings View
        self.settings_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.RadioGroup(
                            content=ft.Column(
                                [
                                    ft.Text("Theme"),
                                    ft.Row(
                                        [
                                            ft.Icon(name=ft.Icons.LIGHT_MODE_OUTLINED),
                                            ft.Radio(value="light", label="Light"),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Icon(name=ft.Icons.DARK_MODE_OUTLINED),
                                            ft.Radio(value="dark", label="Dark"),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                    ),
                                ],
                            ),
                            value="light"
                            if page.theme_mode == ft.ThemeMode.LIGHT
                            else "dark",
                            on_change=self.radiogroup_changed,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            ],
            alignment=ft.CrossAxisAlignment.STRETCH,
        )

        # used by route_change() to set the view matching the route
        self.page_views = {
            "/": ft.View(
                "/",
                [
                    self.drawer,
                    ft.AppBar(
                        title=ft.Text("Home"),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                self.select_task_view,
                                self.empty_tasks_home_view,
                            ],
                            expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                ],
            ),
            "/focus": ft.View(
                "/focus",
                [
                    self.drawer,
                    ft.AppBar(
                        title=ft.Text("Focus Mode"),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                self.focus_mode_view,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                ],
            ),
            "/list": ft.View(
                "/list",
                [
                    self.drawer,
                    ft.AppBar(
                        title=ft.Text("Task List"),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    ),
                    self.task_list_view,
                ],
            ),
            "/settings": ft.View(
                "/settings",
                [
                    self.drawer,
                    ft.AppBar(
                        title=ft.Text("Settings"),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    ),
                    ft.ElevatedButton("Back", on_click=lambda _: page.go("/")),
                    self.settings_view,
                ],
            ),
            "/about": ft.View(
                "/about",
                [
                    self.drawer,
                    ft.AppBar(
                        title=ft.Text("About the app"),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        about["name"],
                                        style=ft.TextThemeStyle.HEADLINE_SMALL,
                                    ),
                                ]
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        f"version: {about['version']}",
                                        style=ft.TextThemeStyle.BODY_LARGE,
                                    ),
                                ]
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        f"Created by: {about['author']}",
                                        style=ft.TextThemeStyle.BODY_MEDIUM,
                                    ),
                                ]
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        about["email"],
                                        style=ft.TextThemeStyle.BODY_MEDIUM,
                                    ),
                                ]
                            ),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Buy me a coffee",
                                        on_click=lambda e: self.open_bmc_url(
                                            e, about["supportme_url"]
                                        ),
                                    )
                                ],
                            ),
                        ],
                        expand=True,
                    ),
                ],
            ),
        }

    def get_task_list_from_db(self):
        task_list_from_db = self.api.list_all_tasks()
        if len(task_list_from_db) > 0:
            return task_list_from_db
        else:
            return []

    def set_task_list(self):
        self.task_list = self.get_task_list_from_db()

    def set_single_task_item(self):
        self.single_task_item = self.get_single_task_item()

    def get_single_task_item(self):
        return self.api.get_next_task() or None

    def defer_task(self, task, e):
        self.api.defer_task(str(task.id))
        e.page.open(ft.SnackBar(ft.Text(f"Deferred: {task.title}")))
        self.single_task_display_text.value = self.get_single_task_item().title
        e.page.update()

    def set_current_focus_task(self, e):
        current_task = self.get_single_task_item()
        self.current_focus_task = current_task
        e.page.open(ft.SnackBar(ft.Text(f"Set Current task: {current_task.title}")))

        self.current_task_display.value = current_task.title
        self.current_task_display.visible = True
        self.focus_mode_title.visible = True
        self.current_task_done_btn.visible = True
        self.empty_current_task_view.visible = False
        e.page.go("/focus")
        e.page.update()

    def finish_current_task(self, e):
        task_to_finish = self.current_focus_task
        self.api.toggle_complete(str(task_to_finish.id))
        e.page.open(ft.SnackBar(ft.Text(f"Win! You completed: {task_to_finish.title}")))

        self.current_focus_task = None
        self.current_task_display.visible = False
        self.current_task_done_btn.visible = False
        self.focus_mode_title.visible = False
        self.empty_current_task_view.visible = True
        self.task_list_control.build()

        if self.get_single_task_item() is not None:
            self.single_task_item = self.get_single_task_item()
            self.single_task_display_text.value = self.single_task_item.title
        else:
            self.select_task_view.visible = False
            self.empty_tasks_home_view.visible = True
            e.page.open(ft.SnackBar(ft.Text("Win: you completed all tasks!")))

        e.page.update()
        e.page.go("/")

    def add_new_task_fab_clicked(self, e):
        e.page.go('/list')

    def handle_drwr_change(self, e):
        e.page.go(self.routes[e.control.selected_index])
        e.open = False

    def radiogroup_changed(self, e):
        e.page.theme_mode = (
            ft.ThemeMode.LIGHT if e.control.value == "light" else ft.ThemeMode.DARK
        )
        e.page.update()

    def route_change(self, route):
        page = route.page
        if page is not None:
            page.views.clear()
            if page.route == "/":
                if self.get_single_task_item() is not None:
                    self.single_task_item = self.get_single_task_item()
                    self.single_task_display_text.value = self.single_task_item.title
                    self.select_task_view.visible = True
                    self.empty_tasks_home_view.visible = False
                else:
                    self.select_task_view.visible = False
                    self.empty_tasks_home_view.visible = True
            page.views.append(self.page_views[page.route])
            page.update()

    def open_bmc_url(self, e, url):
        e.page.launch_url(url)

    def before_update(self):
        self.set_single_task_item()
        self.set_task_list()


def main(page: ft.Page):
    page.title = "Kute Task"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    page.theme_mode = ft.ThemeMode.LIGHT

    # window
    page.window.min_width = 414
    page.window.min_height = 760
    page.window.width = 414
    page.window.height = 760
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER

    page.scroll = ft.ScrollMode.ADAPTIVE

    api = TaskAPI(db_url=sqlite_url)

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    main_app = MainApp(api=api, page=page)
    page.add(main_app)

    page.on_view_pop = view_pop
    page.on_route_change = main_app.route_change
    page.go(page.route)


ft.app(main, view=ft.AppView.WEB_BROWSER)
