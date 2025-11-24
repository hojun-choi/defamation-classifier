package com.defamation.backend.web.dto;

import com.defamation.backend.domain.ClassificationRequest;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.*;

import java.util.Collections;
import java.util.List;

@Getter @Setter
@AllArgsConstructor @NoArgsConstructor
@Builder
public class ClassificationRequestDto {

    private Long id;
    private String problemSituation;

    private List<String> caseNames;

    private String sentenceType;
    private Long sentenceValue;          // 숫자
    private Integer sentenceSuspension;  // 월

    private String sentenceAdditionalOrder;
    private String sentenceReason;
    private String sentenceJudgment;

    public static ClassificationRequestDto from(ClassificationRequest r, ObjectMapper om) {
        return ClassificationRequestDto.builder()
                .id(r.getId())
                .problemSituation(r.getProblemSituation())
                .caseNames(parseList(om, r.getCaseNames()))
                .sentenceType(r.getSentenceType())
                .sentenceValue(r.getSentenceValue())
                .sentenceSuspension(r.getSentenceSuspension())
                .sentenceAdditionalOrder(r.getSentenceAdditionalOrder())
                .sentenceReason(r.getSentenceReason())
                .sentenceJudgment(r.getSentenceJudgment())
                .build();
    }

    private static List<String> parseList(ObjectMapper om, String json) {
        if (json == null || json.isBlank()) return Collections.emptyList();
        try {
            return om.readValue(json, new TypeReference<List<String>>() {});
        } catch (Exception e) {
            return List.of(json);
        }
    }
}
