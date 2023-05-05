-- a SQL script that creates a stored procedure ComputeAverageWeightedScoreForUser that computes and store the average weighted score for a student

DELIMITER |

CREATE PROCEDURE ComputeAverageWeightedScoreForUser(user_id INT)
BEGIN
  UPDATE users SET average_score = (
    SELECT SUM(corrections.score * projects.weight) / SUM(projects.weight) FROM corrections
    JOIN projects ON projects.id = corrections.project_id
    WHERE corrections.user_id = user_id)
  WHERE users.id = user_id;
END;