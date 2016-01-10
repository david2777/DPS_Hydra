CREATE DATABASE  IF NOT EXISTS `hydra` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `hydra`;
-- MySQL dump 10.13  Distrib 5.7.9, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: hydra
-- ------------------------------------------------------
-- Server version	5.7.9-log

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
  `path` varchar(255) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Lists all executeables that can be run by the farm. This is specified when a job is submitted.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_jobboard`
--

DROP TABLE IF EXISTS `hydra_jobboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_jobboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID for the job, Auto Increment by DB on  insertion of job, ',
  `execName` varchar(20) DEFAULT NULL COMMENT 'Executeable the job needs',
  `baseCMD` varchar(255) DEFAULT NULL COMMENT 'The base CMD, ie. -x 1280 -y 720 -cam "TestCam" etc.',
  `startFrame` int(6) DEFAULT '1' COMMENT 'The start frame of the job',
  `endFrame` int(6) DEFAULT '1' COMMENT 'The end frame of the job',
  `byFrame` int(4) DEFAULT '1' COMMENT 'Render each x frame. Caluclated by SubmitterMain for now so we can append the last frame to the frames. Should be editable in FarmView eventually. ',
  `taskFile` varchar(255) DEFAULT NULL COMMENT 'The task file to be rendered ie. the Maya file or PS file or something',
  `priority` int(4) DEFAULT '50' COMMENT 'Priority of the job, higher priority jobs will be executed first',
  `phase` int(4) DEFAULT '0' COMMENT 'Job phase',
  `job_status` char(1) DEFAULT 'U' COMMENT 'Status of the job, for more info on this see MySQLSetup.py',
  `niceName` varchar(60) DEFAULT 'HydraJob' COMMENT 'Nice name of the job for display in FarmView',
  `owner` varchar(45) DEFAULT 'HydraUser' COMMENT 'User name of the person who submitted the job',
  `requirements` varchar(255) DEFAULT NULL COMMENT 'Requirements for the job ie. RedShift, Fusion, MentalRay, Power',
  `creationTime` datetime DEFAULT NULL COMMENT 'Time the job was created',
  `taskDone` int(6) DEFAULT '0' COMMENT 'Total tasks done, calculated and stored by FarmView and RenderNodeMain',
  `totalTask` int(6) DEFAULT '0' COMMENT 'Total subtasks, to avoid querying the subtask DB all the time',
  `maxNodes` int(4) DEFAULT '0' COMMENT 'Max nodes a job should run on',
  `archived` int(4) DEFAULT '0' COMMENT 'Mark a job as archived, 0 = False, 1 = True',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 COMMENT='New job board for Hydra. Setup somewhat differently than the old job board.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_rendernode`
--

DROP TABLE IF EXISTS `hydra_rendernode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_rendernode` (
  `host` varchar(80) NOT NULL COMMENT 'Name of the render node',
  `status` char(1) NOT NULL COMMENT 'The one character abbreviation for the node''s status (Idle, Started, etc)',
  `minPriority` int(11) NOT NULL COMMENT 'Lowest priority task that can be run by this node (Note this also exists in the hydraSettings.cfg file on each node but that one does nothing- David)',
  `task_id` int(11) DEFAULT NULL COMMENT 'The ID of the task currently running (if any)',
  `software_version` varchar(255) DEFAULT NULL COMMENT 'The version of the RenderNodeMain.exe currently running on this node',
  `capabilities` varchar(255) DEFAULT '' COMMENT 'The render nodes current capabilites in alphabetical order. (ie VRay, RenderMan, SOuP)',
  `pulse` datetime DEFAULT NULL COMMENT 'The last time RenderNodeMain.exe was known to be running, if ever',
  `schedule` int(11) DEFAULT '0',
  PRIMARY KEY (`host`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Describes all of the RenderNodes. Made in MySQL Workbench. ';
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
  `command` varchar(1000) DEFAULT NULL COMMENT 'The command to be called by subprocess',
  `status` char(1) DEFAULT NULL COMMENT 'Current task status',
  `createTime` datetime DEFAULT NULL COMMENT 'Time the task was created',
  `startTime` datetime DEFAULT NULL COMMENT 'Time the task started',
  `endTime` datetime DEFAULT NULL COMMENT 'The the task ended',
  `host` varchar(80) DEFAULT NULL COMMENT 'Host the task is running on',
  `exitCode` int(11) DEFAULT NULL COMMENT 'Exit code from the subprocess',
  `logFile` varchar(100) DEFAULT NULL COMMENT 'Log file directory (Local)',
  `requirements` varchar(255) DEFAULT NULL COMMENT 'Requirements to run this task',
  `priority` int(4) DEFAULT NULL COMMENT 'Priority for the task',
  `frame` int(6) DEFAULT NULL COMMENT 'The frame for this task',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8 COMMENT='A new task board for Hydra tasks!';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-01-09 21:21:41
