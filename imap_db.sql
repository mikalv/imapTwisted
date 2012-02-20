-- phpMyAdmin SQL Dump
-- version 3.3.10deb1
-- http://www.phpmyadmin.net
--
-- Serveur: localhost
-- Généré le : Lun 20 Février 2012 à 12:23
-- Version du serveur: 5.1.54
-- Version de PHP: 5.3.5-1ubuntu7.7

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Base de données: `imap_db`
--

-- --------------------------------------------------------

--
-- Structure de la table `imap_flags`
--

CREATE TABLE IF NOT EXISTS `imap_flags` (
  `id_flag` int(6) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id_flag`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=7 ;

--
-- Contenu de la table `imap_flags`
--

INSERT INTO `imap_flags` (`id_flag`, `name`) VALUES
(1, '\\Deleted'),
(4, '\\Answered'),
(3, '\\Seen'),
(5, '\\Draft'),
(6, '\\Recent');

-- --------------------------------------------------------

--
-- Structure de la table `imap_mail_box`
--

CREATE TABLE IF NOT EXISTS `imap_mail_box` (
  `name_mail_box` varchar(50) NOT NULL,
  `uid_validity` int(6) NOT NULL,
  `uid_next` int(6) NOT NULL,
  PRIMARY KEY (`name_mail_box`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Contenu de la table `imap_mail_box`
--

INSERT INTO `imap_mail_box` (`name_mail_box`, `uid_validity`, `uid_next`) VALUES
('greenlamp', 125478, 3);

-- --------------------------------------------------------

--
-- Structure de la table `imap_mail_message`
--

CREATE TABLE IF NOT EXISTS `imap_mail_message` (
  `id_mail_message` int(6) NOT NULL AUTO_INCREMENT,
  `from` varchar(50) NOT NULL,
  `to` varchar(50) NOT NULL,
  `subject` varchar(50) NOT NULL,
  `date` varchar(50) NOT NULL,
  `content` varchar(500) NOT NULL,
  `uid` int(6) NOT NULL,
  `deleted` tinyint(4) NOT NULL,
  `name_mail_box` varchar(50) NOT NULL,
  PRIMARY KEY (`id_mail_message`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Contenu de la table `imap_mail_message`
--

INSERT INTO `imap_mail_message` (`id_mail_message`, `from`, `to`, `subject`, `date`, `content`, `uid`, `deleted`, `name_mail_box`) VALUES
(1, 'greenlamp@localhost', 'greenlamp@localhost', 'objet 1', 'Mon, 13 Feb 2012 13:43:53 +0100 (CET)', 'ceci est un test de contenu', 1, 0, 'greenlamp'),
(2, 'greenlamp@localhost', 'greenlamp@localhost', 'objet 2', 'Mon, 13 Feb 2012 13:43:53 +0100 (CET)', 'Bonjour à tous !', 2, 0, 'greenlamp');

-- --------------------------------------------------------

--
-- Structure de la table `imap_meta_flags`
--

CREATE TABLE IF NOT EXISTS `imap_meta_flags` (
  `uid` int(6) NOT NULL,
  `id_flag` int(6) NOT NULL,
  PRIMARY KEY (`uid`,`id_flag`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Contenu de la table `imap_meta_flags`
--

INSERT INTO `imap_meta_flags` (`uid`, `id_flag`) VALUES
(1, 3);

-- --------------------------------------------------------

--
-- Structure de la table `imap_meta_uids`
--

CREATE TABLE IF NOT EXISTS `imap_meta_uids` (
  `uid_validity` int(6) NOT NULL,
  `uid` int(6) NOT NULL,
  PRIMARY KEY (`uid_validity`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Contenu de la table `imap_meta_uids`
--

INSERT INTO `imap_meta_uids` (`uid_validity`, `uid`) VALUES
(125478, 1);

-- --------------------------------------------------------

--
-- Structure de la table `imap_users`
--

CREATE TABLE IF NOT EXISTS `imap_users` (
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  PRIMARY KEY (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Contenu de la table `imap_users`
--

INSERT INTO `imap_users` (`username`, `password`) VALUES
('greenlamp', 'pass'),
('lanroque', 'pass');
