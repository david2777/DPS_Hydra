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
-- Dumping data for table `hydra_capabilities`
--

LOCK TABLES `hydra_capabilities` WRITE;
/*!40000 ALTER TABLE `hydra_capabilities` DISABLE KEYS */;
INSERT INTO `hydra_capabilities` VALUES ('Fusion'),('FXCache'),('HighPower'),('Maya2014'),('Maya2015'),('Photoshop'),('Redshift');
/*!40000 ALTER TABLE `hydra_capabilities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `hydra_executable`
--

LOCK TABLES `hydra_executable` WRITE;
/*!40000 ALTER TABLE `hydra_executable` DISABLE KEYS */;
INSERT INTO `hydra_executable` VALUES ('maya2014_Render','C:/Program Files/Autodesk/maya2014/bin/render.exe',NULL),('maya2015_Render','C:/Program Files/Autodesk/maya2014/bin/render.exe',NULL);
/*!40000 ALTER TABLE `hydra_executable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `hydra_jobtypes`
--

LOCK TABLES `hydra_jobtypes` WRITE;
/*!40000 ALTER TABLE `hydra_jobtypes` DISABLE KEYS */;
INSERT INTO `hydra_jobtypes` VALUES ('FusionComp'),('MentalRayRender'),('RedshiftRender'),('BatchFile');
/*!40000 ALTER TABLE `hydra_jobtypes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-09-18 18:56:26
