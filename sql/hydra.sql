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
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Lists all executeables that can be run by the farm. This is specified when a job is submitted.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_job`
--

DROP TABLE IF EXISTS `hydra_job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_job` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'The ID number of the job',
  `pickledTicket` text COMMENT 'A text represnetation of the job''s JobTicket object',
  `priority` int(11) DEFAULT NULL COMMENT 'The job''s priority (inherited by its tasks)',
  `project` varchar(45) DEFAULT NULL COMMENT 'The job''s project (inherited by its tasks)',
  `requirements` varchar(255) DEFAULT NULL COMMENT 'The job''s requirements (inherited by its tasks)',
  `createTime` datetime DEFAULT NULL COMMENT 'The time at which the job was created',
  `owner` varchar(45) NOT NULL DEFAULT 'Unknown' COMMENT 'Person who submitted the job',
  `niceName` varchar(60) NOT NULL DEFAULT 'UnknownJobName' COMMENT 'A nice name for the job to be displayed in the job list view. SubmitterMain should default it to be the file name. ',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='Keeps a recored of all submited jobs, which contain one or more task';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_jobboard`
--

DROP TABLE IF EXISTS `hydra_jobboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_jobboard` (
  `job_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID for the job, Auto Increment by DB on  insertion of job, ',
  `baseCMD` varchar(255) DEFAULT NULL COMMENT 'The base CMD, ie. $mayaPath -proj \\\\blah\\blahhh -x 1280 -y 720 etc.',
  `startFrame` smallint(6) DEFAULT '1' COMMENT 'The start frame of the job',
  `endFrame` smallint(6) DEFAULT '1' COMMENT 'The end frame of the job',
  `byFrame` tinyint(4) DEFAULT '1',
  `taskFile` varchar(60) DEFAULT NULL COMMENT 'The task file to be rendered ie. the Maya file or PS file or something',
  `priority` tinyint(4) DEFAULT '50' COMMENT 'Priority of the job, higher priority jobs will be executed first',
  `phase` tinyint(4) DEFAULT '0' COMMENT 'Job phase',
  `job_status` char(1) DEFAULT 'U' COMMENT 'Status of the job, for more info on this see MySQLSetup.py',
  `niceName` varchar(60) DEFAULT 'HydraJob' COMMENT 'Nice name of the job for display in FarmView',
  `owner` varchar(45) DEFAULT 'HydraUser' COMMENT 'User name of the person who submitted the job',
  `requirements` varchar(255) DEFAULT NULL COMMENT 'Requirements for the job ie. RedShift, Fusion, MentalRay, Power',
  `creationTime` datetime DEFAULT NULL,
  PRIMARY KEY (`job_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='New job board for Hydra. Setup somewhat differently than the old job board.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_projects`
--

DROP TABLE IF EXISTS `hydra_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_projects` (
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Lists all current projects.';
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
  PRIMARY KEY (`host`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Describes all of the RenderNodes. Made in MySQL Workbench. ';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_rendertask`
--

DROP TABLE IF EXISTS `hydra_rendertask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_rendertask` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID of the task (different from the job)',
  `status` char(1) DEFAULT NULL COMMENT 'The one character abbreviation for the task''s status (R = Ready, F = Finished, etc)',
  `command` varchar(1000) DEFAULT NULL COMMENT 'The actual command to be executed to perform the task',
  `job_id` int(11) NOT NULL COMMENT 'ID number for the job driving this task',
  `priority` int(11) DEFAULT NULL COMMENT 'Priority for the task (can be different than the job)',
  `project` varchar(45) DEFAULT NULL COMMENT 'The project that the task belongs to',
  `createTime` datetime DEFAULT NULL COMMENT 'Time the task was created',
  `logFile` varchar(45) DEFAULT NULL COMMENT 'Name of the render log file located on the render node under C:\\hydra',
  `host` varchar(80) DEFAULT NULL COMMENT 'Name of the node that is running or ran the task',
  `startTime` datetime DEFAULT NULL COMMENT 'Time the task was started',
  `exitCode` int(11) DEFAULT NULL COMMENT 'Exit code returned by the task (0 = regular, anything else is a possible error)',
  `endTime` datetime DEFAULT NULL COMMENT 'Time the task completed',
  `requirements` varchar(255) DEFAULT NULL COMMENT 'Requirements for the task',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COMMENT='Keeps a record of all render tasks (which are owned by jobs)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hydra_taskboard`
--

DROP TABLE IF EXISTS `hydra_taskboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydra_taskboard` (
  `task_id` int(11) NOT NULL AUTO_INCREMENT,
  `job_id` int(11) NOT NULL,
  `command` varchar(1000) DEFAULT NULL,
  `task_status` char(1) DEFAULT NULL,
  `createTime` datetime DEFAULT NULL,
  `startTime` datetime DEFAULT NULL,
  `endTime` datetime DEFAULT NULL,
  `host` varchar(80) DEFAULT NULL,
  `exitCode` int(11) DEFAULT NULL,
  `logFile` varchar(100) DEFAULT NULL,
  `requirements` varchar(255) DEFAULT NULL,
  `priority` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8 COMMENT='A new task board for Hydra tasks!';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-12-04  0:01:10
