"""
Scrapers para medios colombianos e internacionales
"""
# ── Medios colombianos (nacionales) ──
from scrapers.eltiempo import ElTiempoScraper
from scrapers.elespectador import ElEspectadorScraper
from scrapers.semana import SemanaScraper
from scrapers.lasillavacia import LaSillaVaciaScraper
from scrapers.portafolio import PortafolioScraper
from scrapers.caracol import CaracolScraper
from scrapers.pulzo import PulzoScraper
from scrapers.las2orillas import Las2OrillasScraper

# ── Medios colombianos (regionales) ──
from scrapers.elheraldo import ElHeraldoScraper
from scrapers.elcolombiano import ElColombianoScraper
from scrapers.elpaiscali import ElPaisCaliScraper
from scrapers.vanguardia import VanguardiaScraper
from scrapers.eluniversal import ElUniversalScraper
from scrapers.laopinion import LaOpinionScraper

# ── Internacionales (español) ──
from scrapers.bbc_mundo import BBCMundoScraper
from scrapers.cnn_espanol import CNNEspanolScraper
from scrapers.france24 import France24Scraper
from scrapers.dw_espanol import DWEspanolScraper
from scrapers.infobae import InfobaeScraper
from scrapers.elpais import ElPaisScraper

# ── Internacionales (inglés) ──
from scrapers.reuters import ReutersScraper
from scrapers.ap_news import APNewsScraper
from scrapers.the_guardian import TheGuardianScraper
from scrapers.bloomberg import BloombergScraper
from scrapers.insightcrime import InSightCrimeScraper
from scrapers.colombiareports import ColombiaReportsScraper
from scrapers.nytimes import NYTimesScraper
from scrapers.dw_english import DWEnglishScraper

__all__ = [
    # Colombianos (nacionales)
    'ElTiempoScraper',
    'ElEspectadorScraper',
    'SemanaScraper',
    'LaSillaVaciaScraper',
    'PortafolioScraper',
    'CaracolScraper',
    'PulzoScraper',
    'Las2OrillasScraper',
    # Colombianos (regionales)
    'ElHeraldoScraper',
    'ElColombianoScraper',
    'ElPaisCaliScraper',
    'VanguardiaScraper',
    'ElUniversalScraper',
    'LaOpinionScraper',
    # Internacionales (español)
    'BBCMundoScraper',
    'CNNEspanolScraper',
    'France24Scraper',
    'DWEspanolScraper',
    'InfobaeScraper',
    'ElPaisScraper',
    # Internacionales (inglés)
    'ReutersScraper',
    'APNewsScraper',
    'TheGuardianScraper',
    'BloombergScraper',
    'InSightCrimeScraper',
    'ColombiaReportsScraper',
    'NYTimesScraper',
    'DWEnglishScraper',
]
