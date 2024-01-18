SELECT DISTINCT people.name
FROM stars
JOIN movies ON movies.id = stars.movie_id
JOIN ratings ON ratings.movie_id = movies.id
JOIN stars s2 ON s2.movie_id = movies.id
JOIN people ON people.id = s2.person_id
WHERE people.name != 'Kevin Bacon'
AND movies.id IN (
    SELECT stars.movie_id
    FROM stars
    JOIN people ON people.id = stars.person_id
    WHERE people.name = 'Kevin Bacon' AND people.birth = 1958
);