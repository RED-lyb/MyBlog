-- ============================================================
-- 爱情小窝模块 — 服务器安全建表脚本
-- 数据库：webproject
-- 说明：仅创建爱情小窝相关表，不影响已有业务数据
-- 执行：mysql -u用户 -p webproject < love_nest.sql
-- ============================================================

USE webproject;

-- 清理已废弃的表（若从未创建则无副作用）
DROP TABLE IF EXISTS `love_nest_moments`;

-- 1. 全局配置（单行，id 固定为 1）
CREATE TABLE IF NOT EXISTS `love_nest_config` (
  `id` int unsigned NOT NULL DEFAULT 1 COMMENT '主键，固定为 1',
  `start_date` date DEFAULT NULL COMMENT '在一起的起始日期',
  `slogan` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '爱情口号/副标题',
  `member_user_ids` json DEFAULT NULL COMMENT '可编辑成员用户ID列表，JSON数组，如 [1,2]',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝全局配置表';

INSERT INTO `love_nest_config` (`id`, `start_date`, `slogan`, `member_user_ids`)
VALUES (1, NULL, NULL, JSON_ARRAY())
ON DUPLICATE KEY UPDATE `id` = `id`;

-- 2. 旅行城市（需在 photos 之前创建，供外键引用）
CREATE TABLE IF NOT EXISTS `love_nest_travel_cities` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `adcode` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '市级行政区划代码（国标 adcode）',
  `province_adcode` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '所属省级 adcode',
  `city_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '城市名称',
  `note` text COLLATE utf8mb4_unicode_ci COMMENT '旅行感言/记录',
  `visited_at` date DEFAULT NULL COMMENT '到访日期',
  `created_by` int unsigned DEFAULT NULL COMMENT '创建者用户ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_love_nest_travel_adcode` (`adcode`),
  KEY `idx_love_nest_travel_province` (`province_adcode`),
  KEY `idx_love_nest_travel_visited_at` (`visited_at`),
  CONSTRAINT `love_nest_travel_cities_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝旅行城市表';

-- 3. 照片（相册 person/scenery/food + 旅行 travel）
CREATE TABLE IF NOT EXISTS `love_nest_photos` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '图片文件名，对应 api/static/love_nest/photos/',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '照片标题',
  `caption` text COLLATE utf8mb4_unicode_ci COMMENT '照片描述',
  `category` enum('person','scenery','food','travel') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'person' COMMENT '分类：person-人物, scenery-风景, food-食物, travel-旅行',
  `travel_city_id` int unsigned DEFAULT NULL COMMENT '关联旅行城市ID，相册照片为NULL',
  `sort_order` int NOT NULL DEFAULT 0 COMMENT '排序权重，越大越靠前',
  `created_by` int unsigned DEFAULT NULL COMMENT '上传者用户ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  PRIMARY KEY (`id`),
  KEY `idx_love_nest_photo_category` (`category`),
  KEY `idx_love_nest_photo_travel_city` (`travel_city_id`),
  KEY `idx_love_nest_photo_sort` (`sort_order`),
  KEY `idx_love_nest_photo_created_at` (`created_at`),
  CONSTRAINT `love_nest_photos_ibfk_1` FOREIGN KEY (`travel_city_id`) REFERENCES `love_nest_travel_cities` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `love_nest_photos_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝照片表';

-- 4. 时光（原日记：日期 + 配图 + 一句话）
CREATE TABLE IF NOT EXISTS `love_nest_diaries` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `diary_date` date NOT NULL COMMENT '时光日期',
  `image_filename` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '配图文件名，对应 photos/diary/',
  `sentence` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '一句话',
  `created_by` int unsigned DEFAULT NULL COMMENT '作者用户ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_love_nest_diary_date` (`diary_date`),
  KEY `idx_love_nest_diary_created_by` (`created_by`),
  CONSTRAINT `love_nest_diaries_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝时光表';

-- 5. 纪念日
CREATE TABLE IF NOT EXISTS `love_nest_milestones` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '纪念日名称',
  `milestone_date` date NOT NULL COMMENT '纪念日日期',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '描述',
  `is_yearly` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否每年重复提醒：0-否，1-是',
  `sort_order` int NOT NULL DEFAULT 0 COMMENT '排序权重',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_love_nest_milestone_date` (`milestone_date`),
  KEY `idx_love_nest_milestone_sort` (`sort_order`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝纪念日表';
