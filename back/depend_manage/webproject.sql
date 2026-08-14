-- MySQL dump 10.13  Distrib 8.0.39, for Win64 (x86_64)
--
-- Host: localhost    Database: webproject
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `article_comments`
--

DROP TABLE IF EXISTS `article_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_comments` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `article_id` int unsigned NOT NULL COMMENT '文章ID，外键关联 blog_articles 表',
  `user_id` int unsigned NOT NULL COMMENT '评论用户ID，外键关联 users 表',
  `content` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '评论内容，最多200字',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间，默认服务器系统时间',
  PRIMARY KEY (`id`),
  KEY `idx_article_id` (`article_id`),
  KEY `idx_article_comment_user_id` (`user_id`),
  KEY `idx_article_comment_created_at` (`created_at`),
  CONSTRAINT `article_comments_ibfk_1` FOREIGN KEY (`article_id`) REFERENCES `blog_articles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `article_comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章评论表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`admin`@`localhost`*/ /*!50003 TRIGGER `update_comment_count_on_insert` AFTER INSERT ON `article_comments` FOR EACH ROW BEGIN

    UPDATE blog_articles 

    SET comment_count = comment_count + 1 

    WHERE id = NEW.article_id;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`admin`@`localhost`*/ /*!50003 TRIGGER `update_comment_count_on_delete` AFTER DELETE ON `article_comments` FOR EACH ROW BEGIN

    UPDATE blog_articles 

    SET comment_count = GREATEST(comment_count - 1, 0)

    WHERE id = OLD.article_id;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `blog_articles`
--

DROP TABLE IF EXISTS `blog_articles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `blog_articles` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '文章ID，主键自增',
  `title` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文章标题',
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文章正文，支持 Markdown/HTML',
  `author_id` int unsigned NOT NULL COMMENT '作者ID，外键关联 users 表',
  `view_count` int unsigned NOT NULL DEFAULT '0' COMMENT '浏览量，默认0',
  `love_count` int unsigned NOT NULL DEFAULT '0' COMMENT '喜欢数，默认0',
  `comment_count` int unsigned NOT NULL DEFAULT '0' COMMENT '评论数，默认0，冗余字段便于查询',
  `published_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间，默认服务器系统时间',
  PRIMARY KEY (`id`),
  KEY `idx_author_id` (`author_id`),
  KEY `idx_published_at` (`published_at`),
  KEY `idx_view_count` (`view_count`),
  CONSTRAINT `blog_articles_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='博客文章表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`admin`@`localhost`*/ /*!50003 TRIGGER `update_article_count_on_insert` AFTER INSERT ON `blog_articles` FOR EACH ROW BEGIN

    UPDATE users 

    SET article_count = article_count + 1 

    WHERE id = NEW.author_id;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`admin`@`localhost`*/ /*!50003 TRIGGER `update_article_count_on_delete` AFTER DELETE ON `blog_articles` FOR EACH ROW BEGIN

    UPDATE users 

    SET article_count = article_count - 1 

    WHERE id = OLD.author_id;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `captcha_captchastore`
--

DROP TABLE IF EXISTS `captcha_captchastore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `captcha_captchastore` (
  `id` int NOT NULL AUTO_INCREMENT,
  `challenge` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `response` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hashkey` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expiration` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hashkey` (`hashkey`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `feedbacks`
--

DROP TABLE IF EXISTS `feedbacks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedbacks` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `user_id` int unsigned DEFAULT NULL COMMENT '提出用户ID，外键关联 users 表，NULL表示匿名反馈',
  `issue_type` enum('使用错误','功能建议') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '问题类型：使用错误、功能建议',
  `description` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '问题描述',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '问题提出时间，默认服务器系统时间',
  `is_resolved` enum('未解决','已解决','未采纳') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '未解决' COMMENT '解决状态：未解决、已解决、未采纳',
  `resolved_at` datetime DEFAULT NULL COMMENT '解决时间，未解决时为NULL',
  `author_reply` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '作者回复内容',
  PRIMARY KEY (`id`),
  KEY `idx_feedback_user_id` (`user_id`),
  KEY `idx_issue_type` (`issue_type`),
  KEY `idx_is_resolved` (`is_resolved`),
  KEY `idx_feedback_created_at` (`created_at`),
  CONSTRAINT `feedbacks_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='反馈意见表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `refresh_tokens`
--

DROP TABLE IF EXISTS `refresh_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `refresh_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `token_hash` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Refresh Token的哈希值',
  `expires_at` datetime(6) NOT NULL COMMENT '过期时间',
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `last_used_at` datetime(6) DEFAULT NULL COMMENT '最后使用时间',
  PRIMARY KEY (`id`),
  KEY `refresh_tok_user_id_46676d_idx` (`user_id`),
  KEY `refresh_tok_token_h_2fa7c6_idx` (`token_hash`),
  KEY `refresh_tok_expires_a128d9_idx` (`expires_at`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `update_history`
--

DROP TABLE IF EXISTS `update_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `update_history` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `update_time` date NOT NULL DEFAULT (curdate()) COMMENT '更新日期，默认服务器系统日期',
  `update_content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '更新内容描述',
  PRIMARY KEY (`id`),
  KEY `idx_update_time` (`update_time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='更新历史表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `games`
--

DROP TABLE IF EXISTS `games`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `games` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '卡片标题',
  `content` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '封面图文件名，对应 api/static/games/game_images',
  `introduction` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '卡片底部简介',
  `detail` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '详情描述',
  `web_entry` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Web入口 html，基本与title一致',
  `windows` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Windows 包文件名 game_files/{id}/ 下',
  `linux` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Linux 包文件名',
  `android` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Android 包文件名',
  PRIMARY KEY (`id`),
  KEY `idx_game_title` (`title`(191))
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='趣味游戏表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_follows`
--

DROP TABLE IF EXISTS `user_follows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_follows` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `follower_id` int unsigned NOT NULL COMMENT '关注者ID，外键关联 users 表',
  `following_id` int unsigned NOT NULL COMMENT '被关注者ID，外键关联 users 表',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '关注时间，默认服务器系统时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_follow` (`follower_id`,`following_id`),
  KEY `idx_follower` (`follower_id`),
  KEY `idx_following` (`following_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户关注关系表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`admin`@`localhost`*/ /*!50003 TRIGGER `update_follow_stats_on_insert` AFTER INSERT ON `user_follows` FOR EACH ROW BEGIN

    

    UPDATE users 

    SET follow_count = follow_count + 1 

    WHERE id = NEW.follower_id;

    

    

    UPDATE users 

    SET follower_count = follower_count + 1 

    WHERE id = NEW.following_id;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`admin`@`localhost`*/ /*!50003 TRIGGER `update_follow_stats_on_delete` AFTER DELETE ON `user_follows` FOR EACH ROW BEGIN

    

    UPDATE users 

    SET follow_count = follow_count - 1 

    WHERE id = OLD.follower_id;

    

    

    UPDATE users 

    SET follower_count = follower_count - 1 

    WHERE id = OLD.following_id;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `user_liked_articles`
--

DROP TABLE IF EXISTS `user_liked_articles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_liked_articles` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `user_id` int unsigned NOT NULL COMMENT '用户ID，外键关联 users 表',
  `article_id` int unsigned NOT NULL COMMENT '文章ID，外键关联 blog_articles 表',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '喜欢时间，默认服务器系统时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_like` (`user_id`,`article_id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_article` (`article_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户喜欢的文章关系表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`admin`@`localhost`*/ /*!50003 TRIGGER `update_liked_article_count_on_insert` AFTER INSERT ON `user_liked_articles` FOR EACH ROW BEGIN

    

    UPDATE users 

    SET liked_article_count = liked_article_count + 1 

    WHERE id = NEW.user_id;

    

    

    UPDATE blog_articles 

    SET love_count = love_count + 1 

    WHERE id = NEW.article_id;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`admin`@`localhost`*/ /*!50003 TRIGGER `update_liked_article_count_on_delete` AFTER DELETE ON `user_liked_articles` FOR EACH ROW BEGIN

    

    UPDATE users 

    SET liked_article_count = liked_article_count - 1 

    WHERE id = OLD.user_id;

    

    

    UPDATE blog_articles 

    SET love_count = love_count - 1 

    WHERE id = OLD.article_id;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '登录名，全局唯一',
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '加密后的登录密码',
  `protect` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密保问题原文',
  `answer` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密保答案',
  `registered_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间，默认当前时间',
  `avatar` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像 URL，空表示未上传',
  `bg_color` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '个人中心背景色，CSS 合法值',
  `bg_pattern` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '背景点缀样式',
  `bio` text COLLATE utf8mb4_unicode_ci COMMENT '个人介绍',
  `follow_count` int unsigned NOT NULL DEFAULT '0' COMMENT '关注数，默认0',
  `article_count` int unsigned NOT NULL DEFAULT '0' COMMENT '发布文章数，默认0',
  `liked_article_count` int unsigned NOT NULL DEFAULT '0' COMMENT '喜欢的文章数，默认0',
  `follower_count` int unsigned NOT NULL DEFAULT '0' COMMENT '粉丝数，默认0',
  `is_admin` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否为管理员，0-否，1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `love_nest_config`
--

DROP TABLE IF EXISTS `love_nest_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `love_nest_config` (
  `id` int unsigned NOT NULL DEFAULT '1' COMMENT '主键，固定为 1',
  `start_date` date DEFAULT NULL COMMENT '在一起的起始日期',
  `slogan` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '爱情口号/副标题',
  `member_user_ids` json DEFAULT NULL COMMENT '可编辑成员用户ID列表，JSON数组；管理员始终可编辑',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝全局配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `love_nest_config`
--

LOCK TABLES `love_nest_config` WRITE;
/*!40000 ALTER TABLE `love_nest_config` DISABLE KEYS */;
INSERT INTO `love_nest_config` (`id`, `start_date`, `slogan`, `member_user_ids`) VALUES (1,NULL,NULL,'[]');
/*!40000 ALTER TABLE `love_nest_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `love_nest_travel_cities`
--

DROP TABLE IF EXISTS `love_nest_travel_cities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `love_nest_travel_cities` (
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `love_nest_photos`
--

DROP TABLE IF EXISTS `love_nest_photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `love_nest_photos` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '相对路径，如 person/1.jpg；对应 api/static/love_nest/photos/',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '照片标题',
  `caption` text COLLATE utf8mb4_unicode_ci COMMENT '照片描述',
  `category` enum('person','scenery','food') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'person' COMMENT '相册分类：person-人物, scenery-风景, food-食物',
  `travel_city_id` int unsigned DEFAULT NULL COMMENT '旅行地图关联城市；非空时出现在该城市下',
  PRIMARY KEY (`id`),
  KEY `idx_love_nest_photo_category` (`category`),
  KEY `idx_love_nest_photo_travel_city` (`travel_city_id`),
  CONSTRAINT `love_nest_photos_ibfk_1` FOREIGN KEY (`travel_city_id`) REFERENCES `love_nest_travel_cities` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝照片表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `love_nest_diaries`
--

DROP TABLE IF EXISTS `love_nest_diaries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `love_nest_diaries` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `diary_date` date NOT NULL COMMENT '时光日期',
  `photo_id` int unsigned DEFAULT NULL COMMENT '配图，关联 love_nest_photos.id',
  `sentence` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '一句话',
  PRIMARY KEY (`id`),
  KEY `idx_love_nest_diary_date` (`diary_date`),
  KEY `idx_love_nest_diary_photo` (`photo_id`),
  CONSTRAINT `love_nest_diaries_ibfk_1` FOREIGN KEY (`photo_id`) REFERENCES `love_nest_photos` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝时光表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `love_nest_milestones`
--

DROP TABLE IF EXISTS `love_nest_milestones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `love_nest_milestones` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '纪念日名称',
  `milestone_date` date NOT NULL COMMENT '纪念日日期',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '描述',
  `is_yearly` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否每年重复提醒：0-否，1-是',
  `sort_order` int NOT NULL DEFAULT '0' COMMENT '排序权重，越大越靠前（管理页可配置）',
  PRIMARY KEY (`id`),
  KEY `idx_love_nest_milestone_date` (`milestone_date`),
  KEY `idx_love_nest_milestone_sort` (`sort_order`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爱情小窝纪念日表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-22 23:29:47
