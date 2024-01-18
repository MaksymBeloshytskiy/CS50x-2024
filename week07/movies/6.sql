SELECT AVG(rating)
FROM ratings
JOIN movies m ON movie_id = m.id
WHERE m.year = 2012;