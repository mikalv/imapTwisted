-- phpMyAdmin SQL Dump
-- version 3.4.5deb1
-- http://www.phpmyadmin.net
--
-- Client: localhost
-- Généré le : Mer 22 Février 2012 à 11:59
-- Version du serveur: 5.1.58
-- Version de PHP: 5.3.6-13ubuntu3.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


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
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=7 ;

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
('greenlamp', 125478, 2),
('greenlamp_Trash', 4517376, 1);

-- --------------------------------------------------------

--
-- Structure de la table `imap_mail_folder`
--

CREATE TABLE IF NOT EXISTS `imap_mail_folder` (
  `name_mail_box` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`name_mail_box`,`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Contenu de la table `imap_mail_folder`
--

INSERT INTO `imap_mail_folder` (`name_mail_box`, `name`) VALUES
('greenlamp', 'Inbox'),
('greenlamp', 'Trash');

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
  `content-type` varchar(100) NOT NULL,
  `content` varchar(500) NOT NULL,
  `uid` int(6) NOT NULL,
  `deleted` tinyint(4) NOT NULL,
  `name_mail_box` varchar(50) NOT NULL,
  PRIMARY KEY (`id_mail_message`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Contenu de la table `imap_mail_message`
--

INSERT INTO `imap_mail_message` (`id_mail_message`, `from`, `to`, `subject`, `date`, `content-type`, `content`, `uid`, `deleted`, `name_mail_box`) VALUES
(1, 'greenlamp@localhost', 'greenlamp@localhost', 'objet 1', 'Mon, 13 Feb 2012 13:43:53 +0100 (CET)', 'Content-Type: text/html; charset=iso-8859-1', 'ceci est un test de contenu', 1, 0, 'greenlamp'),
(2, 'greenlamp@localhost', 'greenlamp@localhost', 'objet 2', 'Mon, 13 Feb 2012 13:43:53 +0100 (CET)', 'Content-Type: text/html; charset=iso-8859-1', 'Bonjour à tous !', 2, 0, 'greenlamp');

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
  PRIMARY KEY (`uid_validity`,`uid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Contenu de la table `imap_meta_uids`
--

INSERT INTO `imap_meta_uids` (`uid_validity`, `uid`) VALUES
(125478, 1),
(125478, 2);

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

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
