import flet as ft


def main(page: ft.Page):
    page.title = "Kute Task"

    # must be in the same order as page_views routes
    routes = ["/", "/list", "/new"]

    # Side Drawer
    def handle_dismissal(e):
        pass

    def handle_change(e):
        page.go(routes[e.control.selected_index])
        page.close(drawer)

    def show_drawer(e):
        page.drawer.open = True
        page.drawer.update()

    drawer = ft.NavigationDrawer(
        on_dismiss=handle_dismissal,
        on_change=handle_change,
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="Single Task",
                icon=ft.Icons.EXPLORE,
                selected_icon=ft.Icon(ft.Icons.EXPLORE_OUTLINED),
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                icon=ft.Icon(ft.Icons.LIST_OUTLINED),
                label="List Tasks",
                selected_icon=ft.Icons.LIST,
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icon(ft.Icons.CREATE_OUTLINED),
                label="Add Task",
                selected_icon=ft.Icons.CREATE,
            ),
        ],
    )
    page.drawer = drawer

    # View / : showing only 1 task:
    single_task_view = ft.Column(
        [
            ft.Row(
                [
                    ft.Text(
                        value="What do you want to do now?",
                        theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    ft.Text(
                        value="Orgainize my book shelves",
                        theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                        color=ft.Colors.INDIGO,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
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
                            text_style=ft.TextStyle(size=24)
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    ft.Button(
                        "Defer, show me next",
                        width=300,
                        style=ft.ButtonStyle(
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=2),
                            bgcolor=ft.Colors.GREY_100,
                            color=ft.Colors.GREY_400,
                            text_style=ft.TextStyle(size=24)
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]
    )

    # used by route_change() to set the view matching the route
    page_views = {
        "/": ft.View(
            "/",
            [
                drawer,
                ft.AppBar(
                    title=ft.Text("Focus"),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                ),
                single_task_view,
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

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE


ft.app(main, view=ft.AppView.WEB_BROWSER)
