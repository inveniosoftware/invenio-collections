export class CommunityLinksExtractor {
  #urls;

  constructor(community) {
    if (!community?.links) {
      throw TypeError("Request resource links are undefined");
    }
    this.#urls = community.links;
  }

  get collectionTreesUrl() {
    if (!this.#urls.collection_trees) {
      throw TypeError("Collection trees link missing from resource.");
    }
    return this.#urls.collection_trees;
  }

  get invitationsUrl() {
    if (!this.#urls.invitations) {
      throw TypeError("Invitations link missing from resource.");
    }
    return this.#urls.invitations;
  }

  url(key) {
    const urlOfKey = this.#urls[key];
    if (!urlOfKey) {
      throw TypeError(`"${key}" link missing from resource.`);
    }
    return urlOfKey;
  }
}
