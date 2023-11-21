export type Artist = {
    name : string,
    uris : Map<string, string>,
    image : string,
    birth_date : Date,
    birth_place : string,
    death_date : Date | null,
    death_place : string | null,
    bibliography : string,
    getty_link : string,
    artworks : string[],
}