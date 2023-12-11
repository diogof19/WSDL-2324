export type Artwork = {
    name : string,
    type : string,
    uris : Map<string, string>,
    image : string,
    description : Map<string, string> | null,
    authorUri : Map<string, string> | null,
    authorName : string | null,
    year : string | null,
    wikipedia_link : string | null,
    museumName : string[] | null,
}