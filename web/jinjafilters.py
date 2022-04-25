
def register_filters(app):
    
    @app.template_filter('are_levels_defined')
    def are_levels_defined(players) -> bool:
        return any([pl.level != 4 for pl in players])
    
    @app.template_filter('positionDisplay')
    def positionDisplay(player) -> str:
        if player.pos is None:
            return '-'
        if player.status:
            status = player.status.upper()
            return status if status != "WITHDRAWN" else "WD"

        return player.pos