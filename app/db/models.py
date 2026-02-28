from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean, DateTime, UniqueConstraint, Date
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
from sqlalchemy import Enum

StatutDemande = Enum(
    "brouillon", "soumise", "en_cours", "validee", "refusee", "en_verification",
    name="statut_demande"
)


# ----------------------------
# CLUBS
# ----------------------------
class Club(Base):
    __tablename__ = "clubs"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    raison_sociale = Column(String, nullable=True)
    division = Column(String, nullable=True)
    adresse = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    logo_url = Column(String, nullable=True)

    infos = relationship("ClubInfo", back_populates="club", cascade="all, delete-orphan")
    users = relationship("User", back_populates="club")
    licences = relationship("Licence", back_populates="club")
    federation = relationship("Federation", back_populates="clubs")
    ligue = relationship("Ligue", back_populates="clubs")
    affiliations = relationship("Affiliation", back_populates="club")
    invitations = relationship("Invitation", back_populates="club")
    demandes = relationship("Demande", back_populates="club")
    adherents = relationship("Adherent", back_populates="club")

    federation_id = Column(Integer, ForeignKey('fsbb.federations.id'), nullable=False)
    ligue_id = Column(Integer, ForeignKey('fsbb.ligues.id'), nullable=True)


# ----------------------------
# USERS
# ----------------------------
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    avatar_url = Column(String, nullable=True)

    club_id = Column(Integer, ForeignKey("fsbb.clubs.id"))
    federation_id = Column(Integer, ForeignKey('fsbb.federations.id'), nullable=True)
    ligue_id = Column(Integer, ForeignKey('fsbb.ligues.id'), nullable=True)

    federation = relationship("Federation", back_populates="users")
    ligue = relationship("Ligue", back_populates="users")
    roles = relationship("UserRole", back_populates="user")
    club = relationship("Club", back_populates="users")
    demandes = relationship("Demande", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


# ----------------------------
# LICENCES
# ----------------------------
class Licence(Base):
    __tablename__ = "licences"
    __table_args__ = (
        UniqueConstraint('adherent_id', 'saison_id', name='_unique_licence_par_saison'),
        {'schema': 'fsbb'}
    )

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), unique=True, index=True)
    statut = Column(StatutDemande, nullable=False)
    type_demande = Column(String, nullable=False)

    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    date_naissance = Column(Date, nullable=False)
    categorie_id = Column(Integer, ForeignKey("fsbb.categories.id"), nullable=False)
    club_id = Column(Integer, ForeignKey("fsbb.clubs.id"), nullable=False)
    saison_id = Column(Integer, ForeignKey("fsbb.saisons.id"), nullable=False)
    adherent_id = Column(Integer, ForeignKey("fsbb.adherents.id"), nullable=False)

    date_creation = Column(DateTime, default=datetime.utcnow)
    date_soumission = Column(DateTime, nullable=True)
    date_validation = Column(DateTime, nullable=True)
    date_refus = Column(DateTime, nullable=True)
    commentaire_refus = Column(String, nullable=True)

    # Relations
    club = relationship("Club", back_populates="licences")
    categorie = relationship("Categorie", back_populates="licences")
    fichiers = relationship("Fichier", back_populates="licence", cascade="all, delete-orphan")
    demandes = relationship("Demande", back_populates="licence")
    adherent = relationship("Adherent", back_populates="licences")
    saison = relationship("Saison", back_populates="licences")


# ----------------------------
# CATEGORIES
# ----------------------------
class Categorie(Base):
    __tablename__ = "categories"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, nullable=False)

    licences = relationship("Licence", back_populates="categorie")
    federation_categories = relationship(
        "FederationCategorie", back_populates="categorie", cascade="all, delete-orphan"
    )


# ----------------------------
# TYPES FICHIERS
# ----------------------------
class TypeFichier(Base):
    __tablename__ = "types_fichier"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    fichiers = relationship("Fichier", back_populates="type")


# ----------------------------
# FICHIERS
# ----------------------------
class Fichier(Base):
    __tablename__ = "fichiers"
    __table_args__ = (
        UniqueConstraint('id_licence', 'id_type', name='uq_licence_fichier_unique'),
        {'schema': 'fsbb'}
    )

    id = Column(Integer, primary_key=True, index=True)
    nom_fichier = Column(String, nullable=False)
    chemin = Column(String, nullable=False)
    taille = Column(Integer, nullable=True)
    date_upload = Column(DateTime, default=datetime.utcnow)

    id_licence = Column(Integer, ForeignKey("fsbb.licences.id"), nullable=False)
    id_type = Column(Integer, ForeignKey("fsbb.types_fichier.id"), nullable=False)

    licence = relationship("Licence", back_populates="fichiers")
    type = relationship("TypeFichier", back_populates="fichiers")


# ----------------------------
# INVITATIONS
# ----------------------------
class Invitation(Base):
    __tablename__ = "invitations"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False)
    role = Column(String, default="user")
    club_id = Column(Integer, ForeignKey("fsbb.clubs.id"), nullable=True)
    federation_id = Column(Integer, ForeignKey("fsbb.federations.id"), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    federation = relationship("Federation", back_populates="invitations")
    club = relationship("Club", back_populates="invitations")

    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at


# ----------------------------
# CLUBS INFOS TYPE
# ----------------------------
class ClubInfoType(Base):
    __tablename__ = "clubs_infos_type"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    valeur = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    infos = relationship("ClubInfo", back_populates="type_info")


# ----------------------------
# CLUBS INFOS
# ----------------------------
class ClubInfo(Base):
    __tablename__ = "clubs_infos"
    __table_args__ = (
        UniqueConstraint('club_id', 'id_type', name='uq_club_info_unique'),
        {'schema': 'fsbb'}
    )

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("fsbb.clubs.id"), nullable=False)
    id_type = Column(Integer, ForeignKey("fsbb.clubs_infos_type.id"), nullable=False)
    valeur = Column(String, nullable=True)

    club = relationship("Club", back_populates="infos")
    type_info = relationship("ClubInfoType", back_populates="infos")


# ----------------------------
# FEDERATIONS
# ----------------------------
class Federation(Base):
    __tablename__ = 'federations'
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), unique=True, nullable=False)
    type = Column(Integer, ForeignKey('fsbb.federation_type.id'), nullable=True)

    ligues = relationship("Ligue", back_populates="federation")
    clubs = relationship("Club", back_populates="federation")
    affiliations = relationship("Affiliation", back_populates="federation")
    users = relationship("User", back_populates="federation")
    competitions = relationship("Competition", back_populates="federation")
    federation_categories = relationship("FederationCategorie", back_populates="federation", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="federation")
    saisons = relationship("Saison", back_populates="federation", cascade="all, delete-orphan")
    federation_type = relationship("FederationType", back_populates="federations")

    @property
    def categories(self):
        return [fc.categorie for fc in self.federation_categories]


class FederationType(Base):
    __tablename__ = 'federation_type'
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), unique=True, nullable=False)

    federations = relationship("Federation", back_populates="federation_type")


# ----------------------------
# LIGUES
# ----------------------------
class Ligue(Base):
    __tablename__ = 'ligues'
    __table_args__ = (
        UniqueConstraint('code', 'federation_id', name='uq_ligue_code_fed'),
        {'schema': 'fsbb'}
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False)
    federation_id = Column(Integer, ForeignKey('fsbb.federations.id'), nullable=False)

    federation = relationship("Federation", back_populates="ligues")
    clubs = relationship("Club", back_populates="ligue")
    users = relationship("User", back_populates="ligue")


# ----------------------------
# AFFILIATIONS
# ----------------------------
class Affiliation(Base):
    __tablename__ = 'affiliations'
    __table_args__ = (
        UniqueConstraint('club_id', 'federation_id', 'competition_id', name='uq_affiliation'),
        {'schema': 'fsbb'}
    )

    id = Column(Integer, primary_key=True)
    club_id = Column(Integer, ForeignKey('fsbb.clubs.id'), nullable=False)
    federation_id = Column(Integer, ForeignKey('fsbb.federations.id'), nullable=False)
    competition_id = Column(Integer, ForeignKey('fsbb.competitions.id'), nullable=False)

    status = Column(String(20), default="pending")
    requested_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    club = relationship("Club", back_populates="affiliations")
    federation = relationship("Federation", back_populates="affiliations")
    competition = relationship("Competition", back_populates="affiliations")


# ----------------------------
# ROLES
# ----------------------------
class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))


# ----------------------------
# USER ROLES
# ----------------------------
class UserRole(Base):
    __tablename__ = 'user_roles'
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
        {'schema': 'fsbb'}
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('fsbb.users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('fsbb.roles.id'), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="roles")
    role = relationship("Role")


# ----------------------------
# COMPETITIONS
# ----------------------------
class Competition(Base):
    __tablename__ = 'competitions'
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    description = Column(String(300))

    federation_id = Column(Integer, ForeignKey('fsbb.federations.id'), nullable=False)
    federation = relationship("Federation", back_populates="competitions")
    affiliations = relationship("Affiliation", back_populates="competition")


# ----------------------------
# FEDERATION CATEGORIES
# ----------------------------
class FederationCategorie(Base):
    __tablename__ = "federation_categories"
    __table_args__ = (
        UniqueConstraint('federation_id', 'categorie_id', name='uq_fed_cat'),
        {'schema': 'fsbb'}
    )

    id = Column(Integer, primary_key=True)
    federation_id = Column(Integer, ForeignKey('fsbb.federations.id'), nullable=False)
    categorie_id = Column(Integer, ForeignKey('fsbb.categories.id'), nullable=False)

    federation = relationship("Federation", back_populates="federation_categories")
    categorie = relationship("Categorie", back_populates="federation_categories")


# ----------------------------
# DEMANDES
# ----------------------------
class Demande(Base):
    __tablename__ = "demandes"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    statut = Column(String, default="brouillon", nullable=False)

    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, onupdate=datetime.utcnow)
    date_soumission = Column(DateTime, nullable=True)
    date_validation = Column(DateTime, nullable=True)
    date_refus = Column(DateTime, nullable=True)

    utilisateur_id = Column(Integer, ForeignKey("fsbb.users.id"), nullable=False)
    club_id = Column(Integer, ForeignKey("fsbb.clubs.id"), nullable=False)
    licence_id = Column(Integer, ForeignKey("fsbb.licences.id"), nullable=True)

    commentaires = Column(String, nullable=True)

    user = relationship("User", back_populates="demandes")
    club = relationship("Club", back_populates="demandes")
    licence = relationship("Licence", back_populates="demandes")


class HistoriqueDemande(Base):
    __tablename__ = "demandes_historique"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True)
    demande_id = Column(Integer, ForeignKey("fsbb.demandes.id"), nullable=False)
    ancien_statut = Column(String)
    nouveau_statut = Column(String)
    date_changement = Column(DateTime, default=datetime.utcnow)
    modifie_par_id = Column(Integer, ForeignKey("fsbb.users.id"))

    demande = relationship("Demande", backref="historiques")
    modifie_par = relationship("User")


# ----------------------------
# ADHERENTS
# ----------------------------
class Adherent(Base):
    __tablename__ = "adherents"
    __table_args__ = (
        UniqueConstraint('nom', 'prenom', 'date_naissance', 'club_id', name='_unique_adherent_club'),
        {'schema': 'fsbb'}
    )

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    date_naissance = Column(Date, nullable=False)
    genre = Column(String(10), nullable=True)
    email = Column(String, nullable=True)
    telephone = Column(String, nullable=True)

    club_id = Column(Integer, ForeignKey("fsbb.clubs.id"), nullable=False)
    categorie_id = Column(Integer, ForeignKey("fsbb.categories.id"), nullable=True)

    club = relationship("Club", back_populates="adherents")
    categorie = relationship("Categorie")
    licences = relationship("Licence", back_populates="adherent", uselist=True)

    date_creation = Column(DateTime, default=datetime.utcnow)
    actif = Column(Boolean, default=True)


# ----------------------------
# SAISONS
# ----------------------------
class Saison(Base):
    __tablename__ = "saisons"
    __table_args__ = (
        UniqueConstraint('code', 'federation_id', name='_unique_saison_par_fede'),
        {'schema': 'fsbb'}
    )

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(9), nullable=False)
    federation_id = Column(Integer, ForeignKey("fsbb.federations.id"), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    active = Column(Boolean, default=False)
    date_creation = Column(DateTime, default=datetime.utcnow)

    licences = relationship("Licence", back_populates="saison")
    federation = relationship("Federation", back_populates="saisons")

    def __repr__(self):
        return f"<Saison {self.code}>"
    

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {"schema": "fsbb"}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("fsbb.users.id"), nullable=False)

    titre = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=False)  # licence, match, paiement, system
    lien = Column(String, nullable=True)

    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


# ----------------------------
# OFFRES (Plans tarifaires)
# ----------------------------
StatutDevis = Enum(
    "nouveau", "en_cours", "accepte", "refuse",
    name="statut_devis"
)


class Offre(Base):
    __tablename__ = "offres"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    description = Column(String, nullable=True)
    description_courte = Column(String, nullable=True)
    prix_mensuel = Column(Integer, nullable=True)  # en centimes
    prix_annuel = Column(Integer, nullable=True)    # en centimes
    devise = Column(String(3), default="XOF")
    fonctionnalites = Column(JSON, nullable=True)   # liste de features
    badge = Column(String, nullable=True)            # ex: "Populaire"
    populaire = Column(Boolean, default=False)
    actif = Column(Boolean, default=True)
    ordre = Column(Integer, default=0)
    date_creation = Column(DateTime, default=datetime.utcnow)

    devis_items = relationship("DevisItem", back_populates="offre")


# ----------------------------
# DEVIS (Demandes commerciales)
# ----------------------------
class Devis(Base):
    __tablename__ = "devis"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(20), unique=True, index=True, nullable=False)
    statut = Column(StatutDevis, default="nouveau", nullable=False)

    nom_contact = Column(String, nullable=False)
    email_contact = Column(String, nullable=False)
    telephone_contact = Column(String, nullable=True)
    nom_organisation = Column(String, nullable=True)
    type_organisation = Column(String, nullable=True)  # federation, ligue, club
    message = Column(String, nullable=True)

    date_creation = Column(DateTime, default=datetime.utcnow)
    date_traitement = Column(DateTime, nullable=True)

    items = relationship("DevisItem", back_populates="devis", cascade="all, delete-orphan")


# ----------------------------
# DEVIS ITEMS (Liaison devis ↔ offre)
# ----------------------------
class DevisItem(Base):
    __tablename__ = "devis_items"
    __table_args__ = {'schema': 'fsbb'}

    id = Column(Integer, primary_key=True, index=True)
    devis_id = Column(Integer, ForeignKey("fsbb.devis.id"), nullable=False)
    offre_id = Column(Integer, ForeignKey("fsbb.offres.id"), nullable=False)

    devis = relationship("Devis", back_populates="items")
    offre = relationship("Offre", back_populates="devis_items")
