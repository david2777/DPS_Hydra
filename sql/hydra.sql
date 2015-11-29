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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 COMMENT='Keeps a recored of all submited jobs, which contain one or more task';
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COMMENT='Keeps a record of all render tasks (which are owned by jobs)';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-28 23:16:30
