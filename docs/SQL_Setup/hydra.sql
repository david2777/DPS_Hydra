-- MySQL dump 10.13  Distrib 5.7.17, for Win64 (x86_64)
--
-- Host: 192.168.0.200    Database: hydra
-- ------------------------------------------------------
-- Server version	5.7.18

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `hydra_capabilities`
--

DROP TABLE IF EXISTS `hydra_capabilities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_capabilities` (
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Keeps a record of all specific capabilites (ie, VRay, RenderMan, MentalRay, etc.)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_executable`
--

DROP TABLE IF EXISTS `hydra_executable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_executable` (
  `name` varchar(45) NOT NULL,
  `win32` varchar(255) DEFAULT NULL,
  `linux` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Lists all executeables that can be run by the farm. This is specified when a job is submitted.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_holidays`
--

DROP TABLE IF EXISTS `hydra_holidays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_holidays` (
  `date` char(10) DEFAULT NULL COMMENT 'Date of a holiday, format is YEAR,MONTH,DAY ie. 2015,11,26'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_jobboard`
--

DROP TABLE IF EXISTS `hydra_jobboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_jobboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID for the job, Auto Increment by DB on  insertion of job, ',
  `niceName` varchar(256) NOT NULL DEFAULT 'HydraJob' COMMENT 'Nice name of the job for display in FarmView',
  `projectName` varchar(256) NOT NULL DEFAULT 'UnknownProject' COMMENT 'Nice name for the project. Helps keep the FarmView JobTree organized. ',
  `jobType` varchar(128) NOT NULL,
  `owner` varchar(128) NOT NULL DEFAULT 'HydraUser' COMMENT 'User name of the person who submitted the job',
  `status` char(1) NOT NULL DEFAULT 'U' COMMENT 'Status of the job, for more info on this see MySQLSetup.py',
  `creationTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time the job was created',
  `requirements` varchar(256) NOT NULL DEFAULT '' COMMENT 'Requirements for the job ie. RedShift, Fusion, MentalRay, Power',
  `execName` varchar(64) NOT NULL COMMENT 'Executeable the job needs',
  `baseCMD` varchar(512) NOT NULL COMMENT 'The base CMD, ie. -x 1280 -y 720 -cam "TestCam" etc.',
  `taskFile` varchar(512) NOT NULL COMMENT 'The task file to be rendered ie. the Maya file or PS file or something',
  `priority` int(3) NOT NULL DEFAULT '50' COMMENT 'Priority of the job, higher priority jobs will be executed first',
  `maxNodes` int(2) NOT NULL DEFAULT '0' COMMENT 'Max nodes a job should run on',
  `timeout` int(1) NOT NULL DEFAULT '0' COMMENT 'Timeout measured in seconds per frame, 0 = None',
  `failedNodes` varchar(512) NOT NULL DEFAULT '' COMMENT 'A list of nodes that the job has failed on, each node delimited by a single space. ',
  `attempts` int(1) NOT NULL DEFAULT '0' COMMENT 'Number of times a job has been attempted and failed.',
  `maxAttempts` int(1) NOT NULL DEFAULT '10' COMMENT 'Maximum attempts before a job is stopped as Error.',
  `archived` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Mark a job as archived, 0 = False, 1 = True',
  `phase` int(1) NOT NULL DEFAULT '2',
  `task_total` int(1) NOT NULL DEFAULT '1' COMMENT 'Total number of tasks',
  `task_done` int(1) NOT NULL DEFAULT '0' COMMENT 'Number of tasks complete',
  `startFrame` int(4) DEFAULT NULL COMMENT 'The start frame of the job',
  `endFrame` int(4) DEFAULT NULL COMMENT 'The end frame of the job',
  `byFrame` int(4) DEFAULT NULL COMMENT 'Render each x frame. Caluclated by SubmitterMain for now so we can append the last frame to the frames. Should be editable in FarmView eventually. ',
  `renderLayers` varchar(128) DEFAULT NULL COMMENT 'Render layers seperated by commas',
  `mpf` time DEFAULT NULL COMMENT 'Minute per frame',
  `frameDirectory` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exec_idx` (`execName`),
  KEY `type_idx` (`jobType`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='New job board for Hydra. Setup somewhat differently than the old job board.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_jobtypes`
--

DROP TABLE IF EXISTS `hydra_jobtypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_jobtypes` (
  `type` varchar(64) NOT NULL COMMENT 'Job Type ie RedshiftRender, MentalRayRender, FusionComp',
  PRIMARY KEY (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='A table for storing job types to populate drop down menus and maintain DB integrity. ';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_rendernode`
--

DROP TABLE IF EXISTS `hydra_rendernode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_rendernode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(80) NOT NULL COMMENT 'Name of the render node',
  `status` char(1) NOT NULL DEFAULT 'O' COMMENT 'The one character abbreviation for the node''s status (Idle, Started, etc)',
  `minPriority` int(11) NOT NULL DEFAULT '0' COMMENT 'Lowest priority task that can be run by this node (Note this also exists in the hydraSettings.cfg file on each node but that one does nothing- David)',
  `platform` varchar(15) NOT NULL COMMENT 'System platform (ie win32)',
  `ip_addr` varchar(39) DEFAULT NULL COMMENT 'IP Address for the node, required if the node is enabled for rendering',
  `task_id` int(11) DEFAULT NULL COMMENT 'The ID of the task currently running (if any)',
  `capabilities` varchar(255) DEFAULT '' COMMENT 'The render nodes current capabilites in alphabetical order. (ie VRay, RenderMan, SOuP)',
  `schedule_enabled` int(1) DEFAULT '0',
  `week_schedule` varchar(255) DEFAULT '',
  `pulse` datetime DEFAULT NULL COMMENT 'The last time RenderNodeMain.exe was known to be running, if ever',
  `software_version` varchar(255) DEFAULT NULL COMMENT 'The version of the RenderNodeMain.exe currently running on this node',
  `is_render_node` int(1) DEFAULT '0' COMMENT 'Is this node used for rendering, 0 = False 1 = True',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `host_UNIQUE` (`host`),
  KEY `rendertask_key_idx` (`task_id`),
  CONSTRAINT `rendertask_key` FOREIGN KEY (`task_id`) REFERENCES `hydra_taskboard` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='Describes all of the RenderNodes. Made in MySQL Workbench. ';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_taskboard`
--

DROP TABLE IF EXISTS `hydra_taskboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_taskboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'The task id for this task. Auto incremented and created on submission by DB. ',
  `job_id` int(11) NOT NULL COMMENT 'The job_id for this task. ',
  `status` char(1) NOT NULL DEFAULT 'R' COMMENT 'Current task status',
  `priority` int(3) NOT NULL DEFAULT '50',
  `host` varchar(128) DEFAULT NULL COMMENT 'Host the task is running on',
  `startFrame` int(4) DEFAULT NULL COMMENT 'The start frame for this task',
  `endFrame` int(4) DEFAULT NULL COMMENT 'The end frame for this task',
  `exitCode` int(1) DEFAULT NULL COMMENT 'Exit code from the subprocess',
  `startTime` datetime DEFAULT NULL COMMENT 'Time the task started',
  `endTime` datetime DEFAULT NULL COMMENT 'The the task ended',
  `mpf` time DEFAULT NULL COMMENT 'Minute per frame',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `id_idx` (`job_id`),
  KEY `node_key_idx` (`host`),
  CONSTRAINT `job_id_key` FOREIGN KEY (`job_id`) REFERENCES `hydra_jobboard` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='A new task board for Hydra tasks!';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-04-30 19:52:21
