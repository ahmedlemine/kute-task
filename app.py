import flet as ft
from api import TaskAPI
from db import sqlite_url
from task_list_view import ListTasksView

class Drawer(ft.NavigationDrawer):
    def __init__(self, handle_drwr_change):
        super().__init__()
        self.on_change = handle_drwr_change
        self.controls = [
                ft.Container(height=12),
                ft.NavigationDrawerDestination(
                    label="Choose Task",
                    icon=ft.Icons.EXPLORE,
                    selected_icon=ft.Icon(ft.Icons.EXPLORE_OUTLINED),
                ),
                ft.Divider(thickness=2),
                ft.NavigationDrawerDestination(
                    label="Current Task",
                    icon=ft.Icons.WATCH,
                    selected_icon=ft.Icon(ft.Icons.WATCH_OUTLINED),
                ),
                ft.NavigationDrawerDestination(
                    label="List Tasks",
                    icon=ft.Icon(ft.Icons.LIST_OUTLINED),
                    selected_icon=ft.Icons.LIST,
                ),
                ft.NavigationDrawerDestination(
                    label="Add Task",
                    icon=ft.Icon(ft.Icons.CREATE_OUTLINED),
                    selected_icon=ft.Icons.CREATE,
                ),
            ]


def main(page: ft.Page):
    page.title = "Kute Task"
    api = TaskAPI(db_url=sqlite_url)


    # must be in the same order as page_views routes
    routes = ["/", "/focus", "/list", "/new"]


    def handle_drwr_change(e):
        page.go(routes[e.control.selected_index])
        e.open = False

    drawer = Drawer(handle_drwr_change)
    page.drawer = drawer
    page.update()


    def get_single_task_item():
        next_task = api.get_next_task()
        if next_task is not None:
            return next_task
        return None


    def defer_task(id):
        api.defer_task(str(id))
        single_task_display_text.value = get_single_task_item().title
        page.update()

    def set_current_focus_task(e):
        current_task_display.value = get_single_task_item().title
        page.go("/focus")

    def update_single_task_item():
        single_task_display_text.value = get_single_task_item().title
        page.update()

    def finish_current_task(e):
        task_to_finish = get_single_task_item()
        api.complete_task(str(task_to_finish.id))
        page.add(ft.SnackBar(f"God Job. You've completed task: {task_to_finish.title}"))
        if get_single_task_item() is not None:
            single_task_display_text.value = get_single_task_item().title
        else:
            select_task_view.visible = False
            empty_tasks_home_view.visible = True
        page.go("/")
        page.update()

    # View / : selecting a task to do now:
    single_task_display_text = ft.Text(
        value=get_single_task_item().title
        if get_single_task_item() is not None
        else "no remaining tasks",
        theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
        max_lines=3,
        width=320,
        text_align=ft.TextAlign.CENTER,
        style=ft.TextStyle(overflow=ft.TextOverflow.VISIBLE),
    )

    select_task_view = ft.Column(
        [
            ft.Row(
                [
                    ft.Text(
                        value="What do you want to do now?",
                        theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(  # temp empty spacing
                height=60
            ),
            ft.Row(
                [single_task_display_text],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(  # temp empty spacing
                height=10
            ),
            ft.Row(
                [
                    ft.ElevatedButton(
                        text="Do Now!",
                        on_click=set_current_focus_task,
                        width=300,
                        style=ft.ButtonStyle(
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=2),
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
                    ft.TextButton(
                        "Defer, show me the next",
                        on_click=lambda _: defer_task(get_single_task_item().id),
                        width=300,
                        style=ft.ButtonStyle(
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=2),
                            bgcolor=ft.Colors.GREY_300,
                            color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(size=24),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.CrossAxisAlignment.STRETCH,
        visible=get_single_task_item() is not None,
    )
    # View /focus : focusing on only 1 task that's being done now:
    current_task_display = ft.Text(
        value=get_single_task_item().title
        if get_single_task_item() is not None
        else "no remaining tasks",
        max_lines=5,
        width=320,
        text_align=ft.TextAlign.CENTER,
        theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
        style=ft.TextStyle(overflow=ft.TextOverflow.VISIBLE),
    )

    empty_tasks_home_view = ft.Column(
        [
            ft.Row(
                [
                    ft.Text(
                        value="No unfinished tasks to select from. Please add somet tasks to start.",
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        max_lines=5,
                        width=320,
                        text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(overflow=ft.TextOverflow.VISIBLE),
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.CrossAxisAlignment.STRETCH,
        visible=get_single_task_item() is None,
    )

    focus_mode_view = ft.Column(
        [
            ft.Row(
                [
                    ft.Text(
                        value="currently wroking on:",
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        style=ft.TextStyle(color=ft.Colors.GREY_600),
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [current_task_display],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(  # temp empty spacing
                height=200
            ),
            ft.Row(
                [
                    ft.TextButton(
                        "Done",
                        on_click=finish_current_task,
                        width=300,
                        visible=get_single_task_item() is not None,
                        style=ft.ButtonStyle(
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=2),
                            bgcolor=ft.Colors.GREY_300,
                            color=ft.Colors.GREY_600,
                            text_style=ft.TextStyle(size=24),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.CrossAxisAlignment.STRETCH,
    )

    # Task list view:
    task_list_control = ListTasksView()
    task_list_view = ft.Row([task_list_control])
    # used by route_change() to set the view matching the route
    page_views = {
        "/": ft.View(
            "/",
            [
                drawer,
                ft.AppBar(
                    title=ft.Text("Home"),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                ),
                select_task_view,
                empty_tasks_home_view,
            ],
        ),
        "/focus": ft.View(
            "/focus",
            [
                drawer,
                ft.AppBar(
                    title=ft.Text("Focus Mode"),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                ),
                focus_mode_view,
            ],
        ),
        "/list": ft.View(
            "/list",
            [
                drawer,
                ft.AppBar(
                    title=ft.Text("Task List"),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                ),
                task_list_view,
            ],
        ),
        "/new": ft.View(
            "/new",
            [
                drawer,
                ft.AppBar(
                    title=ft.Text("New Task"),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                ),
                ft.ElevatedButton("Back", on_click=lambda _: page.go("/")),
            ],
        ),
    }

    def route_change(route):
        page.views.clear()
        page.views.append(page_views[page.route])
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    # window
    page.window.min_width = 414
    page.window.min_height = 760
    page.window.width = 414
    page.window.height = 760
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER

    page.scroll = ft.ScrollMode.ADAPTIVE


ft.app(main, view=ft.AppView.WEB_BROWSER)
