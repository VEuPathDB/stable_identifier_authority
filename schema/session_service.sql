-- MySQL Script generated by MySQL Workbench
-- Fri Oct  2 11:54:35 2020
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema session_service
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema session_service
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `session_service` DEFAULT CHARACTER SET utf8 ;
USE `session_service` ;

-- -----------------------------------------------------
-- Table `session_service`.`assigning_application`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `session_service`.`assigning_application` ;

CREATE TABLE IF NOT EXISTS `session_service`.`assigning_application` (
  `application_id` INT NOT NULL AUTO_INCREMENT,
  `application_name` VARCHAR(500) NOT NULL,
  `version` VARCHAR(45) NOT NULL,
  `description` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`application_id`),
  UNIQUE INDEX `application_name` (`application_name` ASC, `version` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `session_service`.`session`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `session_service`.`session` ;

CREATE TABLE IF NOT EXISTS `session_service`.`session` (
  `session_id` INT NOT NULL AUTO_INCREMENT,
  `ses_application_id` INT NOT NULL,
  `database_name` VARCHAR(500) NOT NULL,
  `osid_idsetid` INT NOT NULL DEFAULT 0 COMMENT 'The OSID web-service id range starts at 1. 0 denotes that this id was not generated by OSID ',
  `data_check` ENUM('pass', 'fail', 'pending') NOT NULL DEFAULT 'pending',
  `message` BLOB NOT NULL,
  `creation_date` DATETIME NOT NULL,
  PRIMARY KEY (`session_id`),
  INDEX `application_id_idx` (`ses_application_id` ASC) VISIBLE,
  CONSTRAINT `session_application_id`
    FOREIGN KEY (`ses_application_id`)
    REFERENCES `session_service`.`assigning_application` (`application_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `session_service`.`stable_identifier_record`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `session_service`.`stable_identifier_record` ;

CREATE TABLE IF NOT EXISTS `session_service`.`stable_identifier_record` (
  `stable_identifier_record_id` INT NOT NULL AUTO_INCREMENT,
  `stable_identifier` VARCHAR(100) NOT NULL,
  `status` ENUM('current', 'obsolete') NOT NULL DEFAULT 'current',
  `sie_session_id` INT NOT NULL,
  `feature_type` ENUM('gene', 'transcript', 'translation') NULL,
  PRIMARY KEY (`stable_identifier_record_id`),
  INDEX `session_id_idx` (`sie_session_id` ASC) VISIBLE,
  UNIQUE INDEX `name_status` (`stable_identifier` ASC, `status` ASC) VISIBLE,
  CONSTRAINT `event_session_id`
    FOREIGN KEY (`sie_session_id`)
    REFERENCES `session_service`.`session` (`session_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
