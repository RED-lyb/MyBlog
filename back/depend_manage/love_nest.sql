-- ============================================================
-- 爱情小窝模块 — 建表脚本（新环境 / 全量初始化）
-- 数据库：webproject
-- 执行：mysql -u用户 -p webproject < love_nest.sql
--
-- 表关系（图片均来自 love_nest_photos 相册）：
--   love_nest_config          单行全局配置
--   love_nest_travel_cities   已访城市
--   love_nest_photos          相册；travel_city_id 关联城市（一对多：一城多图）
--   love_nest_diaries         时光；photo_id 关联相册（一对一：一条一图）
--   love_nest_milestones      纪念日（sort_order 可在管理页配置）
--
-- ============================================================

USE webproject;

DROP TABLE IF EXISTS `love_nest_moments`;

CREATE TABLE IF NOT EXISTS `love_nest_config` (
  `id` int unsigned NOT NULL DEFAULT 1 COMMENT '主键，固定为 1',
  `start_date` date DEFAULT NULL COMMENT '在一起的起始日期',
  `slogan` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '爱情口号/副标题',
  `member_user_ids` json DEFAULT NULL COMMENT '可编辑成员用户ID列表，JSON 数组；管理员始终可编辑',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝全局配置表';

INSERT INTO `love_nest_config` (`id`, `start_date`, `slogan`, `member_user_ids`)
VALUES (1, NULL, NULL, JSON_ARRAY())
ON DUPLICATE KEY UPDATE `id` = `id`;

CREATE TABLE IF NOT EXISTS `love_nest_travel_cities` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `adcode` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '市级行政区划代码（国标 adcode）',
  `province_adcode` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '所属省级 adcode（6 位，如 110000）',
  `city_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '城市名称',
  `note` text COLLATE utf8mb4_unicode_ci COMMENT '旅行感言/备注',
  `visited_at` date DEFAULT NULL COMMENT '到访日期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_love_nest_travel_adcode` (`adcode`),
  KEY `idx_love_nest_travel_province` (`province_adcode`),
  KEY `idx_love_nest_travel_visited_at` (`visited_at`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝旅行城市表';

CREATE TABLE IF NOT EXISTS `love_nest_photos` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '相对路径，如 person/1.jpg；对应 api/static/love_nest/photos/',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '照片标题',
  `caption` text COLLATE utf8mb4_unicode_ci COMMENT '照片描述',
  `category` enum('person','scenery','food') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'person' COMMENT '相册分类：person-人物, scenery-风景, food-食物',
  `travel_city_id` int unsigned DEFAULT NULL COMMENT '旅行地图关联城市；非空时出现在该城市下（与相册 category 独立）',
  PRIMARY KEY (`id`),
  KEY `idx_love_nest_photo_category` (`category`),
  KEY `idx_love_nest_photo_travel_city` (`travel_city_id`),
  CONSTRAINT `love_nest_photos_ibfk_1` FOREIGN KEY (`travel_city_id`) REFERENCES `love_nest_travel_cities` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝照片表';

CREATE TABLE IF NOT EXISTS `love_nest_diaries` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `diary_date` date NOT NULL COMMENT '时光日期',
  `photo_id` int unsigned DEFAULT NULL COMMENT '配图，关联 love_nest_photos.id',
  `sentence` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '一句话',
  PRIMARY KEY (`id`),
  KEY `idx_love_nest_diary_date` (`diary_date`),
  KEY `idx_love_nest_diary_photo` (`photo_id`),
  CONSTRAINT `love_nest_diaries_ibfk_1` FOREIGN KEY (`photo_id`) REFERENCES `love_nest_photos` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝时光表';

CREATE TABLE IF NOT EXISTS `love_nest_milestones` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '纪念日名称',
  `milestone_date` date NOT NULL COMMENT '纪念日日期',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '描述',
  `is_yearly` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否每年重复提醒：0-否，1-是',
  `sort_order` int NOT NULL DEFAULT 0 COMMENT '排序权重，越大越靠前（管理页可配置）',
  PRIMARY KEY (`id`),
  KEY `idx_love_nest_milestone_date` (`milestone_date`),
  KEY `idx_love_nest_milestone_sort` (`sort_order`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝纪念日表';
