-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 3.111.126.92    Database: elearn
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `course_courserequest`
--

DROP TABLE IF EXISTS `course_courserequest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_courserequest` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `level` varchar(50) NOT NULL,
  `department` varchar(255) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `course_id` bigint NOT NULL,
  `hod_id` bigint NOT NULL,
  `program_id` bigint NOT NULL,
  `team_member_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `course_courserequest_course_id_176a7b41_fk_course_course_id` (`course_id`),
  KEY `course_courserequest_hod_id_344fb043_fk_accounts_user_id` (`hod_id`),
  KEY `course_courserequest_program_id_bd2375df_fk_course_program_id` (`program_id`),
  KEY `course_courserequest_team_member_id_680cc9d3_fk_accounts_user_id` (`team_member_id`),
  CONSTRAINT `course_courserequest_course_id_176a7b41_fk_course_course_id` FOREIGN KEY (`course_id`) REFERENCES `course_course` (`id`),
  CONSTRAINT `course_courserequest_hod_id_344fb043_fk_accounts_user_id` FOREIGN KEY (`hod_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `course_courserequest_program_id_bd2375df_fk_course_program_id` FOREIGN KEY (`program_id`) REFERENCES `course_program` (`id`),
  CONSTRAINT `course_courserequest_team_member_id_680cc9d3_fk_accounts_user_id` FOREIGN KEY (`team_member_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-24 14:43:24
