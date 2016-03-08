# -*- coding: utf-8 -*-
# import ogr, osr
import math

def toFloat(s):
        try:
            s = s.replace(",",".")
            s=float(s)
        except ValueError:
            pass 
        except TypeError:
            pass     
        except AttributeError:
            pass             
        return s


# inom	imin	imax	elt	esout	etounnel	phi_dr	c_dr	phi_tr	c_tr	phi_un	c_un	k0	n
def cob_step_1(z_ref, ref_stratus, sigma_v ):
    th = ref_stratus.POINTS.top.coordinates[2] - z_ref
    sigma_v += th*ref_stratus.PARAMETERS.inom
    return sigma_v

# inom	imin	imax	elt	esout	etounnel	phi_dr	c_dr	phi_tr	c_tr	phi_un	c_un	k0	n
def cob_step_2(z_ref, ref_stratus,sigma_v,z_wt, z_tun, gamma_muck):
    pCob = 0.0
    # se non ho falda
    p_wt  = max((0,(z_wt - z_ref)*9.81))
    sigma_v_eff = sigma_v - p_wt
    phi = math.radians(ref_stratus.PARAMETERS.phi_tr)
    ci = ref_stratus.PARAMETERS.c_tr
    ka = (1.- math.sin(phi))/(1+math.sin(phi))
    sigma_ha_eff = sigma_v_eff * ka - 2.*ci*math.sqrt(ka)
    pCob = sigma_ha_eff + p_wt + 20.0 + (z_tun-z_ref)*gamma_muck
    return pCob        
        
        
        
"""        
def latLonToProjection(lat, lon, epsg):
    '''
    Converte le coordinate nel formato latitudine, longitudine (EPSG 4326)
    in coordinate del sistema di riferimento specificato tramite il suo EPSG
    per i documenti della Grand Paris l'EPSG è 3949
    '''
    LATLON_EPSG = 4326
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lat, lon)
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(LATLON_EPSG)
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(epsg)
    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    point.Transform(coordTransform)
    return (point.GetX(), point.GetY())
    
"""