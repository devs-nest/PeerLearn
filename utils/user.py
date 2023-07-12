async def get_dm_channel(member):
    if not member.dm_channel:
        await member.create_dm()
    return member.dm_channel


def get_member_group_details_from_roles(member):
    team = None
    is_team_leader = False
    is_vice_team_leader = False
    batch_leader_groups = []
    flag = "Team"
    for role in member.roles:
        start = len(role.name) - len(flag)
        if role.name[start:] == flag:
            if role.name[:2] == "BL":
                batch_leader_groups.append(role.name[3:])
            else:
                team = role.name
        if role.name == "Team Leaders":
            is_team_leader = True
        if role.name == "Vice Team Leaders":
            is_vice_team_leader = True
    return team, is_team_leader, is_vice_team_leader, batch_leader_groups
