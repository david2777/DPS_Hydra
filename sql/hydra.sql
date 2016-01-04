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
-- Dumping data for table `hydra_capabilities`
--

LOCK TABLES `hydra_capabilities` WRITE;
/*!40000 ALTER TABLE `hydra_capabilities` DISABLE KEYS */;
INSERT INTO `hydra_capabilities` VALUES ('Fusion'),('FXCache'),('HighPower'),('Houdini'),('Maya2014'),('Maya2015'),('MentalRay'),('Photoshop'),('Redshift'),('RenderMan'),('SOuP');
/*!40000 ALTER TABLE `hydra_capabilities` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `hydra_executable`
--

LOCK TABLES `hydra_executable` WRITE;
/*!40000 ALTER TABLE `hydra_executable` DISABLE KEYS */;
INSERT INTO `hydra_executable` VALUES ('maya2014_Proper','C:/Program Files/Autodesk/maya2014/bin/maya.exe'),('maya2014_Render','C:/Program Files/Autodesk/maya2014/bin/render.exe'),('maya2015_Render','C:/Program Files/Autodesk/maya2015/bin/render.exe');
/*!40000 ALTER TABLE `hydra_executable` ENABLE KEYS */;
UNLOCK TABLES;

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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COMMENT='New job board for Hydra. Setup somewhat differently than the old job board.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hydra_jobboard`
--

LOCK TABLES `hydra_jobboard` WRITE;
/*!40000 ALTER TABLE `hydra_jobboard` DISABLE KEYS */;
INSERT INTO `hydra_jobboard` VALUES (1,'maya2014_Render',' -proj F:/Projects/Fruits/ -x 640 -y 360',101,110,10,'F:/Projects/Fruits/scenes/orangeSliceTest.ma',62,1,'R','orangeSliceTest.ma_Phase01','dduvoisin','%%','2016-01-03 20:21:30',0,2,1),(2,'maya2014_Render',' -proj F:/Projects/Fruits/',101,110,1,'F:/Projects/Fruits/scenes/orangeSliceTest.ma',50,2,'U','orangeSliceTest.ma_Phase02','dduvoisin','%%','2016-01-03 20:21:30',0,10,1);
/*!40000 ALTER TABLE `hydra_jobboard` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `hydra_rendernode`
--

LOCK TABLES `hydra_rendernode` WRITE;
/*!40000 ALTER TABLE `hydra_rendernode` DISABLE KEYS */;
INSERT INTO `hydra_rendernode` VALUES ('DAVIDPC','I',50,NULL,'C:\\Users\\David\\Documents\\GitHub\\DPS_Hydra\\RenderNodeMain.py','Maya2014 Maya2015 Quixel Redshift SOUP Substance','2016-01-03 20:01:41',1);
/*!40000 ALTER TABLE `hydra_rendernode` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8 COMMENT='A new task board for Hydra tasks!';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hydra_taskboard`
--

LOCK TABLES `hydra_taskboard` WRITE;
/*!40000 ALTER TABLE `hydra_taskboard` DISABLE KEYS */;
INSERT INTO `hydra_taskboard` VALUES (1,1,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -x 640 -y 360 -mr:v 5 -s 101 -e 101 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','R','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',62,101),(2,1,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -x 640 -y 360 -mr:v 5 -s 110 -e 110 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',62,110),(3,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 101 -e 101 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,101),(4,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 102 -e 102 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,102),(5,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 103 -e 103 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,103),(6,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 104 -e 104 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,104),(7,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 105 -e 105 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,105),(8,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 106 -e 106 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,106),(9,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 107 -e 107 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,107),(10,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 108 -e 108 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,108),(11,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 109 -e 109 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,109),(12,2,'C:/Program Files/Autodesk/maya2014/bin/render.exe  -proj F:/Projects/Fruits/ -mr:v 5 -s 110 -e 110 \"F:/Projects/Fruits/scenes/orangeSliceTest.ma\"','U','2016-01-03 20:21:30',NULL,NULL,NULL,NULL,NULL,'%%',50,110);
/*!40000 ALTER TABLE `hydra_taskboard` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-01-03 20:44:28
