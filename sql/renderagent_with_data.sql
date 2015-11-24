CREATE DATABASE  IF NOT EXISTS `renderagent` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `renderagent`;
-- MySQL dump 10.13  Distrib 5.7.9, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: renderagent
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
-- Table structure for table `renderagent_capabilities`
--

DROP TABLE IF EXISTS `renderagent_capabilities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `renderagent_capabilities` (
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Keeps a record of all specific capabilites (ie, VRay, RenderMan, MentalRay, etc.)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `renderagent_capabilities`
--

LOCK TABLES `renderagent_capabilities` WRITE;
/*!40000 ALTER TABLE `renderagent_capabilities` DISABLE KEYS */;
/*!40000 ALTER TABLE `renderagent_capabilities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `renderagent_executable`
--

DROP TABLE IF EXISTS `renderagent_executable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `renderagent_executable` (
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Lists all executeables that can be run by the farm. This is specified when a job is submitted.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `renderagent_executable`
--

LOCK TABLES `renderagent_executable` WRITE;
/*!40000 ALTER TABLE `renderagent_executable` DISABLE KEYS */;
/*!40000 ALTER TABLE `renderagent_executable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `renderagent_job`
--

DROP TABLE IF EXISTS `renderagent_job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `renderagent_job` (
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
-- Dumping data for table `renderagent_job`
--

LOCK TABLES `renderagent_job` WRITE;
/*!40000 ALTER TABLE `renderagent_job` DISABLE KEYS */;
INSERT INTO `renderagent_job` VALUES (1,'(iJobTicket\nMaya2014\np0\n(dp1\nS\'priority\'\np2\nI50\nsS\'endFrame\'\np3\nI1\nsS\'mayaProjectPath\'\np4\nS\'F:/Projects/Fruits/\'\np5\nsS\'project\'\np6\nS\'DPS\'\np7\nsS\'sceneFile\'\np8\nS\'F:/Projects/Fruits/scenes/orangeSliceTest.ma\'\np9\nsS\'startFrame\'\np10\nI1\nsS\'capability_pattern\'\np11\nS\'%Redshift%\'\np12\nsS\'batchSize\'\np13\nI1\nsb.',50,'DPS','%Redshift%','2015-11-20 22:10:41','dduvoisin','TestScene1');
/*!40000 ALTER TABLE `renderagent_job` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `renderagent_projects`
--

DROP TABLE IF EXISTS `renderagent_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `renderagent_projects` (
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Lists all current projects.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `renderagent_projects`
--

LOCK TABLES `renderagent_projects` WRITE;
/*!40000 ALTER TABLE `renderagent_projects` DISABLE KEYS */;
/*!40000 ALTER TABLE `renderagent_projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `renderagent_rendernode`
--

DROP TABLE IF EXISTS `renderagent_rendernode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `renderagent_rendernode` (
  `host` varchar(80) NOT NULL COMMENT 'Name of the render node',
  `status` char(1) NOT NULL COMMENT 'The one character abbreviation for the node''s status (Idle, Started, etc)',
  `minPriority` int(11) NOT NULL COMMENT 'Lowest priority task that can be run by this node (Note this also exists in the renderagentSettings.cfg file on each node but that one does nothing- David)',
  `task_id` int(11) DEFAULT NULL COMMENT 'The ID of the task currently running (if any)',
  `software_version` varchar(255) DEFAULT NULL COMMENT 'The version of the RenderNodeMain.exe currently running on this node',
  `capabilities` varchar(255) DEFAULT '' COMMENT 'The render nodes current capabilites in alphabetical order. (ie VRay, RenderMan, SOuP)',
  `pulse` datetime DEFAULT NULL COMMENT 'The last time RenderNodeMain.exe was known to be running, if ever',
  PRIMARY KEY (`host`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Describes all of the RenderNodes. Made in MySQL Workbench. ';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `renderagent_rendernode`
--

LOCK TABLES `renderagent_rendernode` WRITE;
/*!40000 ALTER TABLE `renderagent_rendernode` DISABLE KEYS */;
INSERT INTO `renderagent_rendernode` VALUES ('DAVIDPC','O',50,NULL,'C:\\Users\\David\\Documents\\GitHub\\DPS_RenderAgent\\RenderNodeMain.py','','2015-11-23 22:24:16');
/*!40000 ALTER TABLE `renderagent_rendernode` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `renderagent_rendertask`
--

DROP TABLE IF EXISTS `renderagent_rendertask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `renderagent_rendertask` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID of the task (different from the job)',
  `status` char(1) DEFAULT NULL COMMENT 'The one character abbreviation for the task''s status (R = Ready, F = Finished, etc)',
  `command` varchar(1000) DEFAULT NULL COMMENT 'The actual command to be executed to perform the task',
  `job_id` int(11) NOT NULL COMMENT 'ID number for the job driving this task',
  `priority` int(11) DEFAULT NULL COMMENT 'Priority for the task (can be different than the job)',
  `project` varchar(45) DEFAULT NULL COMMENT 'The project that the task belongs to',
  `createTime` datetime DEFAULT NULL COMMENT 'Time the task was created',
  `logFile` varchar(45) DEFAULT NULL COMMENT 'Name of the render log file located on the render node under C:\\renderagent',
  `host` varchar(80) DEFAULT NULL COMMENT 'Name of the node that is running or ran the task',
  `startTime` datetime DEFAULT NULL COMMENT 'Time the task was started',
  `exitCode` int(11) DEFAULT NULL COMMENT 'Exit code returned by the task (0 = regular, anything else is a possible error)',
  `endTime` datetime DEFAULT NULL COMMENT 'Time the task completed',
  `requirements` varchar(255) DEFAULT NULL COMMENT 'Requirements for the task',
  `phase` int(11) DEFAULT NULL COMMENT 'Phase that job belongs to',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COMMENT='Keeps a record of all render tasks (which are owned by jobs)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `renderagent_rendertask`
--

LOCK TABLES `renderagent_rendertask` WRITE;
/*!40000 ALTER TABLE `renderagent_rendertask` DISABLE KEYS */;
INSERT INTO `renderagent_rendertask` VALUES (1,'F','[\'c:\\\\program files\\\\autodesk\\\\maya2014\\\\bin\\\\render.exe\', \'-mr:v\', \'5\', \'-s\', \'1\', \'-e\', \'1\', \'-proj\', \'F:/Projects/Fruits/\', \'F:/Projects/Fruits/scenes/orangeSliceTest.ma\']',1,50,'DPS','2015-11-20 22:10:41',NULL,NULL,NULL,NULL,NULL,NULL,1),(2,'F','[\'c:\\\\program files\\\\autodesk\\\\maya2014\\\\bin\\\\render.exe\', \'-mr:v\', \'5\', \'-s\', \'1\', \'-e\', \'1\', \'-proj\', \'F:/Projects/Fruits/\', \'F:/Projects/Fruits/scenes/orangeSliceTest.ma\']',1,50,'DPS','2015-11-20 22:10:41',NULL,NULL,NULL,NULL,NULL,NULL,2),(3,'F','[\'c:\\\\program files\\\\autodesk\\\\maya2014\\\\bin\\\\render.exe\', \'-mr:v\', \'5\', \'-s\', \'1\', \'-e\', \'1\', \'-proj\', \'F:/Projects/Fruits/\', \'F:/Projects/Fruits/scenes/orangeSliceTest.ma\']',1,50,'DPS','2015-11-20 22:10:41',NULL,NULL,NULL,NULL,NULL,NULL,2),(4,'F','[\'c:\\\\program files\\\\autodesk\\\\maya2014\\\\bin\\\\render.exe\', \'-mr:v\', \'5\', \'-s\', \'1\', \'-e\', \'1\', \'-proj\', \'F:/Projects/Fruits/\', \'F:/Projects/Fruits/scenes/orangeSliceTest.ma\']',1,50,'DPS','2015-11-20 22:10:41',NULL,NULL,NULL,NULL,NULL,NULL,3),(5,'F','[\'c:\\\\program files\\\\autodesk\\\\maya2014\\\\bin\\\\render.exe\', \'-mr:v\', \'5\', \'-s\', \'1\', \'-e\', \'1\', \'-proj\', \'F:/Projects/Fruits/\', \'F:/Projects/Fruits/scenes/orangeSliceTest.ma\']',1,50,'DPS','2015-11-20 22:10:41',NULL,NULL,NULL,NULL,NULL,NULL,3),(6,'F','[\'c:\\\\program files\\\\autodesk\\\\maya2014\\\\bin\\\\render.exe\', \'-mr:v\', \'5\', \'-s\', \'1\', \'-e\', \'1\', \'-proj\', \'F:/Projects/Fruits/\', \'F:/Projects/Fruits/scenes/orangeSliceTest.ma\']',1,50,'DPS','2015-11-20 22:10:41',NULL,NULL,NULL,NULL,NULL,NULL,4);
/*!40000 ALTER TABLE `renderagent_rendertask` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-24  0:16:32
