import flet as ft
from api import TaskAPI
from db import sqlite_url
from models import Task


def main(page: ft.Page):
    page.title = "Kute Task"

    # must be in the same order as page_views routes
    routes = ["/", "/focus", "/list", "/new"]
    api = TaskAPI(db_url=sqlite_url)

    single_task_item = api.get_next_task()

    # Side Drawer
    def handle_drwr_dismissal(e):
        pass

    def handle_drwr_change(e):
        page.go(routes[e.control.selected_index])
        page.close(drawer)

    def show_drawer(e):
        page.drawer.open = True
        page.drawer.update()

    drawer = ft.NavigationDrawer(
        on_dismiss=handle_drwr_dismissal,
        on_change=handle_drwr_change,
        controls=[
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
        ],
    )
    page.drawer = drawer

    # View / : selecting a task to do now:
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
                [
                    ft.Text(
                        value=single_task_item.title,
                        theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                        color=ft.Colors.WHITE,
                        max_lines=3,
                        style=ft.TextStyle(overflow=ft.TextOverflow.VISIBLE),
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(  # temp empty spacing
                height=10
            ),
            ft.Row(
                [
                    ft.ElevatedButton(
                        text="Do Now!",
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
                        width=300,
                        style=ft.ButtonStyle(
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=2),
                            bgcolor=ft.Colors.GREY_100,
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
    # View /focus : focusing on only 1 task that's being done now:
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
                [
                    ft.Text(
                        value=single_task_item.title,
                        max_lines=3,
                        theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                        color=ft.Colors.WHITE,
                        style=ft.TextStyle(overflow=ft.TextOverflow.VISIBLE),
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(  # temp empty spacing
                height=200
            ),
            ft.Row(
                [
                    ft.TextButton(
                        "Done",
                        width=300,
                        style=ft.ButtonStyle(
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=2),
                            bgcolor=ft.Colors.GREY_100,
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
                ft.ElevatedButton("Back", on_click=lambda _: page.go("/")),
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
    page.window.max_height = 960
    page.window.max_width = 400
    page.window.min_height = 600
    page.window.min_width = 360
    page.window.width = 414
    page.window.height = 760
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER

    page.scroll = ft.ScrollMode.ADAPTIVE


ft.app(main, view=ft.AppView.WEB_BROWSER)
