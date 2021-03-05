# 系统固定角色ID
ROLE_ROOT_ID = 1              # 系统root角色,此角色只能有一个用户使用
ROLE_ADMIN_ID = 2             # 默认管理员角色，注册用户为自己组织的管理员，

# 系统固定组织ID
GROUP_SYS_ADMIN_ID = 1 # 总部组织ID

# 组织类型
GROUP_KIND_PERSONAL = 1 # 个人
GROUP_KIND_GROUP = 2    # 团体/企业

# 验证码
VERIFY_CODE_LENGTH = 6
VERIFY_CODE_EXPIRE_TIME = 60*5

# status
STATE_INVALID = 0
STATE_VALID = 1
STATE_DELETED = 2