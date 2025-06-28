-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1:3306
-- Время создания: Июн 28 2025 г., 03:38
-- Версия сервера: 5.7.39
-- Версия PHP: 7.2.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `ADDY`
--

-- --------------------------------------------------------

--
-- Структура таблицы `agent_learning_data`
--

CREATE TABLE `agent_learning_data` (
  `id` int(11) NOT NULL,
  `agent_id` int(11) NOT NULL,
  `data_type` enum('message_history','profile_interaction','preferences') DEFAULT NULL,
  `data_content` json NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `agent_simulations`
--

CREATE TABLE `agent_simulations` (
  `id` int(11) NOT NULL,
  `conversation_id` int(11) NOT NULL,
  `agent1_id` int(11) NOT NULL,
  `agent2_id` int(11) NOT NULL,
  `simulation_status` enum('pending','in_progress','completed','failed') DEFAULT 'pending',
  `compatibility_score` decimal(3,2) DEFAULT NULL,
  `simulation_summary` text,
  `started_at` timestamp NULL DEFAULT NULL,
  `completed_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `agent_simulation_feedback`
--

CREATE TABLE `agent_simulation_feedback` (
  `id` int(11) NOT NULL,
  `simulation_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `accuracy_rating` tinyint(4) DEFAULT NULL,
  `usefulness_rating` tinyint(4) DEFAULT NULL,
  `feedback_text` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `agent_simulation_messages`
--

CREATE TABLE `agent_simulation_messages` (
  `id` int(11) NOT NULL,
  `simulation_id` int(11) NOT NULL,
  `sender_agent_id` int(11) NOT NULL,
  `message_text` text NOT NULL,
  `sentiment_score` decimal(3,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `chat_conversations`
--

CREATE TABLE `chat_conversations` (
  `id` int(11) NOT NULL,
  `match_id` int(11) NOT NULL,
  `last_message_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `chat_messages`
--

CREATE TABLE `chat_messages` (
  `id` int(11) NOT NULL,
  `conversation_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `message_text` text NOT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `message_type` enum('user','agent_simulation') DEFAULT 'user',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `matches`
--

CREATE TABLE `matches` (
  `id` int(11) NOT NULL,
  `user1_id` int(11) NOT NULL,
  `user2_id` int(11) NOT NULL,
  `match_status` enum('active','paused','ended') DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `profile_details`
--

CREATE TABLE `profile_details` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `age` int(11) DEFAULT NULL,
  `gender` varchar(32) DEFAULT NULL,
  `interests` text,
  `bio` text,
  `profile_photo_url` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `last_activity` timestamp NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `user_agents`
--

CREATE TABLE `user_agents` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `personality_data` json NOT NULL,
  `learning_status` enum('learning','ready','updating') DEFAULT 'learning',
  `last_updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `user_conversation_feedback`
--

CREATE TABLE `user_conversation_feedback` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `conversation_id` int(11) NOT NULL,
  `rating` tinyint(4) DEFAULT NULL,
  `feedback_text` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `user_likes`
--

CREATE TABLE `user_likes` (
  `id` int(11) NOT NULL,
  `from_user_id` int(11) NOT NULL,
  `to_user_id` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `user_preferences`
--

CREATE TABLE `user_preferences` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `age_min` int(11) DEFAULT NULL,
  `age_max` int(11) DEFAULT NULL,
  `preferred_genders` json DEFAULT NULL,
  `preferred_distance` int(11) DEFAULT NULL,
  `other_preferences` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `user_sessions`
--

CREATE TABLE `user_sessions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `fingerprint_hash` varchar(64) NOT NULL,
  `jwt_token_hash` varchar(64) NOT NULL,
  `expires_at` timestamp NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `agent_learning_data`
--
ALTER TABLE `agent_learning_data`
  ADD PRIMARY KEY (`id`),
  ADD KEY `agent_id` (`agent_id`);

--
-- Индексы таблицы `agent_simulations`
--
ALTER TABLE `agent_simulations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `conversation_id` (`conversation_id`),
  ADD KEY `agent1_id` (`agent1_id`),
  ADD KEY `agent2_id` (`agent2_id`),
  ADD KEY `idx_agent_simulations_status` (`simulation_status`,`created_at`);

--
-- Индексы таблицы `agent_simulation_feedback`
--
ALTER TABLE `agent_simulation_feedback`
  ADD PRIMARY KEY (`id`),
  ADD KEY `simulation_id` (`simulation_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Индексы таблицы `agent_simulation_messages`
--
ALTER TABLE `agent_simulation_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_agent_id` (`sender_agent_id`),
  ADD KEY `idx_agent_simulation_messages_simulation` (`simulation_id`,`created_at`);

--
-- Индексы таблицы `chat_conversations`
--
ALTER TABLE `chat_conversations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `match_id` (`match_id`),
  ADD KEY `idx_chat_conversations_last_message` (`last_message_at`);

--
-- Индексы таблицы `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `idx_chat_messages_conversation` (`conversation_id`,`created_at`);

--
-- Индексы таблицы `matches`
--
ALTER TABLE `matches`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_match` (`user1_id`,`user2_id`),
  ADD KEY `user2_id` (`user2_id`),
  ADD KEY `idx_matches_users` (`user1_id`,`user2_id`,`match_status`);

--
-- Индексы таблицы `profile_details`
--
ALTER TABLE `profile_details`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `idx_profile_details_gender` (`gender`),
  ADD KEY `idx_profile_details_age` (`age`),
  ADD KEY `idx_profile_details_location` (`location`);

--
-- Индексы таблицы `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_users_last_activity` (`last_activity`);

--
-- Индексы таблицы `user_agents`
--
ALTER TABLE `user_agents`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_agent` (`user_id`);

--
-- Индексы таблицы `user_conversation_feedback`
--
ALTER TABLE `user_conversation_feedback`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_conversation_feedback` (`user_id`,`conversation_id`),
  ADD KEY `conversation_id` (`conversation_id`);

--
-- Индексы таблицы `user_likes`
--
ALTER TABLE `user_likes`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_like` (`from_user_id`,`to_user_id`),
  ADD KEY `idx_user_likes_to_user` (`to_user_id`,`created_at`);

--
-- Индексы таблицы `user_preferences`
--
ALTER TABLE `user_preferences`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_preferences` (`user_id`);

--
-- Индексы таблицы `user_sessions`
--
ALTER TABLE `user_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `jwt_token_hash` (`jwt_token_hash`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `agent_learning_data`
--
ALTER TABLE `agent_learning_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `agent_simulations`
--
ALTER TABLE `agent_simulations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `agent_simulation_feedback`
--
ALTER TABLE `agent_simulation_feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `agent_simulation_messages`
--
ALTER TABLE `agent_simulation_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `chat_conversations`
--
ALTER TABLE `chat_conversations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `chat_messages`
--
ALTER TABLE `chat_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `matches`
--
ALTER TABLE `matches`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `profile_details`
--
ALTER TABLE `profile_details`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `user_agents`
--
ALTER TABLE `user_agents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `user_conversation_feedback`
--
ALTER TABLE `user_conversation_feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `user_likes`
--
ALTER TABLE `user_likes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `user_preferences`
--
ALTER TABLE `user_preferences`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `user_sessions`
--
ALTER TABLE `user_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `agent_learning_data`
--
ALTER TABLE `agent_learning_data`
  ADD CONSTRAINT `agent_learning_data_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `user_agents` (`id`);

--
-- Ограничения внешнего ключа таблицы `agent_simulations`
--
ALTER TABLE `agent_simulations`
  ADD CONSTRAINT `agent_simulations_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversations` (`id`),
  ADD CONSTRAINT `agent_simulations_ibfk_2` FOREIGN KEY (`agent1_id`) REFERENCES `user_agents` (`id`),
  ADD CONSTRAINT `agent_simulations_ibfk_3` FOREIGN KEY (`agent2_id`) REFERENCES `user_agents` (`id`);

--
-- Ограничения внешнего ключа таблицы `agent_simulation_feedback`
--
ALTER TABLE `agent_simulation_feedback`
  ADD CONSTRAINT `agent_simulation_feedback_ibfk_1` FOREIGN KEY (`simulation_id`) REFERENCES `agent_simulations` (`id`),
  ADD CONSTRAINT `agent_simulation_feedback_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `agent_simulation_messages`
--
ALTER TABLE `agent_simulation_messages`
  ADD CONSTRAINT `agent_simulation_messages_ibfk_1` FOREIGN KEY (`simulation_id`) REFERENCES `agent_simulations` (`id`),
  ADD CONSTRAINT `agent_simulation_messages_ibfk_2` FOREIGN KEY (`sender_agent_id`) REFERENCES `user_agents` (`id`);

--
-- Ограничения внешнего ключа таблицы `chat_conversations`
--
ALTER TABLE `chat_conversations`
  ADD CONSTRAINT `chat_conversations_ibfk_1` FOREIGN KEY (`match_id`) REFERENCES `matches` (`id`);

--
-- Ограничения внешнего ключа таблицы `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversations` (`id`),
  ADD CONSTRAINT `chat_messages_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `matches`
--
ALTER TABLE `matches`
  ADD CONSTRAINT `matches_ibfk_1` FOREIGN KEY (`user1_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `matches_ibfk_2` FOREIGN KEY (`user2_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `profile_details`
--
ALTER TABLE `profile_details`
  ADD CONSTRAINT `profile_details_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `user_agents`
--
ALTER TABLE `user_agents`
  ADD CONSTRAINT `user_agents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `user_conversation_feedback`
--
ALTER TABLE `user_conversation_feedback`
  ADD CONSTRAINT `user_conversation_feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `user_conversation_feedback_ibfk_2` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversations` (`id`);

--
-- Ограничения внешнего ключа таблицы `user_likes`
--
ALTER TABLE `user_likes`
  ADD CONSTRAINT `user_likes_ibfk_1` FOREIGN KEY (`from_user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `user_likes_ibfk_2` FOREIGN KEY (`to_user_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `user_preferences`
--
ALTER TABLE `user_preferences`
  ADD CONSTRAINT `user_preferences_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `user_sessions`
--
ALTER TABLE `user_sessions`
  ADD CONSTRAINT `user_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
