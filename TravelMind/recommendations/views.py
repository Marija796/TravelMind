from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from destinations.models import Destination
from destinations.serializers import DestinationSerializer


def score_destination(destination, user):
    score = 0
    breakdown = {
        'type_match': 0,
        'budget_fit': 0,
        'season_match': 0,
        'activity_overlap': 0,
    }

    if user.preferred_travel_type and destination.travel_type == user.preferred_travel_type:
        breakdown['type_match'] = 40

    if user.budget and destination.estimated_cost <= user.budget:
        breakdown['budget_fit'] = 30

    if user.preferred_season and destination.best_season == user.preferred_season:
        breakdown['season_match'] = 20

    if user.preferred_activities and destination.activities:
        user_set = set(user.preferred_activities)
        dest_set = set(destination.activities)
        overlap_count = len(user_set & dest_set)
        breakdown['activity_overlap'] = min(overlap_count * 10, 30)

    score = sum(breakdown.values())
    return score, breakdown


def generate_explanation(destination, user, breakdown):
    reasons = []

    if breakdown['type_match'] > 0:
        type_label = destination.travel_type.replace('_', ' ')
        reasons.append(f"it matches your {type_label} travel style")

    if breakdown['budget_fit'] > 0 and user.budget:
        reasons.append(f"fits your ${int(user.budget):,} budget at ${int(destination.estimated_cost):,}")

    if breakdown['season_match'] > 0 and destination.best_season:
        reasons.append(f"is best visited in {destination.best_season} (your preferred season)")

    if breakdown['activity_overlap'] > 0 and user.preferred_activities and destination.activities:
        matching = sorted(set(user.preferred_activities) & set(destination.activities))
        if len(matching) == 1:
            reasons.append(f"offers {matching[0]} from your interests")
        elif len(matching) == 2:
            reasons.append(f"offers {matching[0]} and {matching[1]} from your interests")
        else:
            reasons.append(f"offers {', '.join(matching[:-1])}, and {matching[-1]} from your interests")

    if not reasons:
        return ""

    if len(reasons) == 1:
        return f"Recommended because {reasons[0]}."
    elif len(reasons) == 2:
        return f"Recommended because {reasons[0]}, and {reasons[1]}."
    else:
        joined = ', '.join(reasons[:-1])
        return f"Recommended because {joined}, and {reasons[-1]}."


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        destinations = Destination.objects.all()

        scored = []
        for dest in destinations:
            score, breakdown = score_destination(dest, user)
            if score > 0:
                scored.append((score, breakdown, dest))

        scored.sort(key=lambda x: x[0], reverse=True)

        serializer = DestinationSerializer(
            [item[2] for item in scored],
            many=True,
            context={'request': request}
        )

        results = []
        for i, item in enumerate(scored):
            data = dict(serializer.data[i])
            data['score'] = item[0]
            data['score_breakdown'] = item[1]
            data['match_explanation'] = generate_explanation(item[2], user, item[1])
            results.append(data)

        return Response({
            'count': len(results),
            'results': results,
        })


class AnonymousRecommendationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        travel_type = request.query_params.get('travel_type', '')
        budget = request.query_params.get('budget', '')
        season = request.query_params.get('season', '')
        activities_raw = request.query_params.get('activities', '')
        activities = [a.strip() for a in activities_raw.split(',') if a.strip()] if activities_raw else []

        budget_float = float(budget) if budget else None

        class GuestPrefs:
            preferred_travel_type = travel_type
            preferred_season = season
            preferred_activities = activities
            budget = budget_float

        prefs = GuestPrefs()
        destinations = Destination.objects.all()

        scored = []
        for dest in destinations:
            score, breakdown = score_destination(dest, prefs)
            if score > 0:
                scored.append((score, breakdown, dest))

        scored.sort(key=lambda x: x[0], reverse=True)

        serializer = DestinationSerializer(
            [item[2] for item in scored],
            many=True,
            context={'request': request}
        )

        results = []
        for i, item in enumerate(scored):
            data = dict(serializer.data[i])
            data['score'] = item[0]
            data['score_breakdown'] = item[1]
            data['match_explanation'] = generate_explanation(item[2], prefs, item[1])
            results.append(data)

        return Response({
            'count': len(results),
            'results': results,
        })
